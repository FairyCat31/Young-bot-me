"""
Logger 0.1a
"""
from datetime import datetime
from app.scripts.components.jsonmanager import JsonManager, AddressType
from colorama import init, Fore, Style
init()

"""
Usage:
printf(text_print, suffix_id{0: info, 1:warn, 2:error}, log_text_in_file)
Example:
from logger import Logger, TypeLogText
l = Logger('TestModule')

l.printf('hello world!')
l.printf('some annoying and popular warn', type_message=TypeLogText., log_text_in_file=False)
"""


class LogType:
    """
    helpful class for set log suffix in func printf
    """
    INFO = 0
    WARN = 1
    ERROR = 2


# main class of this module
class Logger:
    def __init__(self, module_prefix: str):
        # get conf to logger
        jsm = JsonManager(address_type=AddressType.FILE, file_name_or_path="logger_conf.json")
        jsm.load_from_file()
        self.logger_conf = jsm.get_buffer()
        # init class data, prefix
        self.module_prefix = module_prefix
        self.__old_date = ""
        self.__path_to_log_file = ""
        self.color_suffixes = [Fore.CYAN, Fore.YELLOW, Fore.RED]
        self.suffixes = ["INFO ", "WARN ", "ERROR"]

    def __str__(self):
        return self.module_prefix

    @staticmethod
    def __get_str_datetime(time, datetime_format: str) -> str:
        return time.strftime(datetime_format)

    # add note to file
    def __add_note(self, line: str, new_date: str):
        # check if change the date
        if self.__old_date != new_date:
            # create new file
            self.__path_to_log_file = f"{self.logger_conf['default_path']}{self.module_prefix}_{new_date}.txt"
            with open(self.__path_to_log_file, "w", encoding=self.logger_conf["encoding"]) as file:
                file.write(f"Logger version {self.logger_conf['version']} | Log of module --> {self.module_prefix}\n")
            self.__old_date = new_date
        # write a note to the file
        with open(self.__path_to_log_file, "a", encoding=self.logger_conf["encoding"]) as file:
            file.write(line)

    # print info
    def printf(self, line: str, log_type: int = 0, log_text_in_file: bool = True):
        # generate timestamp, prefix and suffix
        now_int_time = datetime.now()
        now_date = self.__get_str_datetime(now_int_time, self.logger_conf["date_format"])
        now_time = self.__get_str_datetime(now_int_time, self.logger_conf["time_format"])
        suffix = self.suffixes[log_type]
        # generate color text
        f_line = (f"{Style.BRIGHT}[{Fore.CYAN}{now_time}{Fore.RESET}]{Style.RESET_ALL} " +
                  f"{Style.BRIGHT}[{Fore.GREEN}{self.module_prefix}{Fore.RESET}]{Style.RESET_ALL} " +
                  f"{Style.BRIGHT}[{self.color_suffixes[log_type]}{suffix}{Fore.RESET}]{Style.RESET_ALL} "
                  f"{Style.BRIGHT}{line}")

        print(f_line)

        # if need to save note in file
        if log_text_in_file:
            # generate text without ansi color
            f_line = f"[{now_time}] [{self.module_prefix}] [{suffix}] {line}\n"
            self.__add_note(f_line, now_date)
