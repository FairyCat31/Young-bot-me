from datetime import datetime
from app.scripts.utils.ujson import JsonManager, AddressType
from sys import stdout, path as sys_path
from typing import TextIO
from colorama import init, Fore, Style
from pathlib import Path
init()

launch_path = sys_path[1]


class LogType:
    """
    helpful class for set log suffix in func printf
    """
    INFO = 0
    DEBUG = 1
    WARN = 2
    ERROR = 3
    FATAL = 4


class Colors:
    """
    Color themes for logger output
    """
    time = f"{Style.BRIGHT}[{Fore.CYAN}{{now_time}}{Fore.RESET}]"
    name = f"[{Fore.GREEN}{{name}}{Fore.RESET}]"
    log_types = ["INFO ", "DEBUG", "WARN ", "ERROR", "FATAL"]
    color_log_types = [
        f"{Style.BRIGHT}[{Fore.CYAN}INFO {Fore.RESET}]",
        f"{Style.BRIGHT}[{Fore.GREEN}DEBUG{Fore.RESET}]",
        f"{Style.BRIGHT}[{Fore.YELLOW}WARN {Fore.RESET}]",
        f"{Style.BRIGHT}[{Fore.RED}ERROR{Fore.RESET}]",
        f"{Style.BRIGHT}[{Fore.RED}FATAL{Fore.RESET}]"]
    color_line = ["{line}", "{line}", "{line}", "{line}", f"{Fore.RED}{{line}}{Fore.RESET}"]


# main class of this module
class Logger:
    """
    Class for logging all info with timestamps, file saving and coloring
    """
    def __init__(self, name: str, debug_mode: bool = None,  out_stream: TextIO = None):
        """
        name - this is a prefix, which logger will use
        debug_mode - if logger need to skip DEBUG message
        """
        # get conf to logger
        self.cfg = JsonManager(AddressType.FILE, "logger_conf.json")
        self.cfg.load_from_file()
        self.out_stream = out_stream
        if out_stream is None:
            self.out_stream = stdout.orig_out_stream if isinstance(stdout, PrintHandler) else stdout
        self._debug_mode = debug_mode
        # init class data, prefix
        self.name = name
        self.__old_date = ""
        self.__path_to_log_file = ""
        self.msg_format = self.cfg["msg_format"] + Fore.RESET

    def __str__(self):
        return self.name

    @property
    def debug_mode(self) -> bool:
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, value: bool):
        self._debug_mode = value

    @staticmethod
    def __get_str_datetime(time, datetime_format: str) -> str:
        return time.strftime(datetime_format)

    # add note to file
    def __add_note(self, line: str, new_date: str | None):
        # check if change the date
        if self.__old_date != new_date:
            # create new file
            fullpath = f"{launch_path}/{self.cfg['default_path']}"
            Path(fullpath).mkdir(parents=True, exist_ok=True)
            self.__path_to_log_file = f"{fullpath}{self.name}_{new_date}.txt"
            with open(self.__path_to_log_file, "w", encoding=self.cfg["encoding"]) as file:
                file.write(f"Logger version | Log of module --> {self.name}\n")
            self.__old_date = new_date
        # write a note to the file
        with open(self.__path_to_log_file, "a", encoding=self.cfg["encoding"]) as file:
            file.write(line)

    # print info
    def printf(self,
               line: str,
               log_type: int = 0,
               end: str = "\n",
               watermark: bool = True,
               log_text_in_file: bool = True):
        """ PRINT ONE LINE"""
        now_int_time = datetime.now()
        now_date = self.__get_str_datetime(now_int_time, self.cfg["date_format"])
        now_time = self.__get_str_datetime(now_int_time, self.cfg["time_format"])
        # generate timestamp
        if watermark:
            # generate color text
            c_line = self.msg_format.format(now_time=Colors.time.format(now_time=now_time),
                                            name=Colors.name.format(name=self.name),
                                            log_type=Colors.color_log_types[log_type],
                                            line=Colors.color_line[log_type].format(line=line))
        else:
            c_line = Colors.color_line[log_type].format(line=line)
        print(c_line, file=self.out_stream, end=end)
        # need to save note in file
        if log_text_in_file:
            # generate text without ansi color
            if watermark:
                f_line = self.msg_format.format(now_time=now_time,
                                                name=self.name,
                                                log_type=Colors.log_types[log_type],
                                                line=line
                                                ) + end
            else:
                f_line = line + end
            # add text to file
            self.__add_note(f_line, now_date)

    def println(self,
                *lines: str,
                log_type: int = 0,
                end: str = "\n",
                watermark: bool = True,
                log_text_in_file: bool = True):
        """ PRINT MANY LINES"""
        for line in lines:
            self.printf(line, log_type=log_type, end=end, watermark=watermark, log_text_in_file=log_text_in_file)


class PrintHandler:
    """ Class for the handling stdout stream"""
    def __init__(self, logger: Logger, orig_out_stream: TextIO = stdout,
                 save_to_file: bool = False):
        """
            logger - Bot logger object
            orig_out_stream - original stdout object
            save_to_file - is need to save DEBUG messages in file
        """
        self.log = logger
        self._orig_out_stream = orig_out_stream
        self._out_text = ""
        self.save_to_file = save_to_file

    @property
    def orig_out_stream(self) -> TextIO:
        return self._orig_out_stream

    def flush(self):
        pass

    def write(self, message: str | bytes):
        if not message:
            return
        if type(message) is bytes:
            message = message.decode()
        self._out_text += message
        if message[-1] == "\n":
            self.log.printf(self._out_text, LogType.DEBUG, end="", log_text_in_file=self.save_to_file)
            self._out_text = ""
            return


class ErrorHandler:
    """ Class for the handling stdout stream"""
    def __init__(self, logger: Logger):
        """ logger - Bot logger object """
        self.log = logger

    def flush(self):
        pass

    def write(self, message):
        if not message:
            return
        str_msg = str(message)
        if str_msg.find("\n") != -1:
            lines = str_msg.split("\n")
            self.log.printf(lines[0], log_type=LogType.FATAL, watermark=False)
            self.log.println(*[lines[i] for i in range(1, len(lines)-1)], log_type=LogType.FATAL)
            self.log.printf(lines[-1], log_type=LogType.FATAL, end="")
        else:
            self.log.printf(message, log_type=LogType.FATAL, watermark=False, end="")