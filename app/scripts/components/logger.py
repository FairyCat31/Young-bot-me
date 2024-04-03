"""
Logger 0.1a
"""
from datetime import datetime
from os.path import exists, dirname
from os import makedirs


_version = "0.1a"
_default_path = "data/logs/"
_time_format = "[%d.%m.%Y %H:%M:%S]"
_simple_time_format = "[%H:%M:%S]"
_time_format_file = "%d-%m-%Y-%H-%M-%S"


def get_str_datetime(datetime_format: str) -> str:
    return datetime.now().strftime(datetime_format)


class Logger:
    def __init__(self, name: str, file_name: str):
        self.name = name
        self.log = ""
        self.file_path = _default_path + file_name + get_str_datetime(_time_format_file) + ".txt"
        self.save_check_file(self.file_path)

    def __str__(self):
        return self.name

    def save_check_file(self, path: str, is_need_create_file=True) -> bool:
        result = exists(path)

        if is_need_create_file and not result:
            makedirs(dirname(path), exist_ok=True)
            file = open(path, "w", encoding="utf-8")
            file.write(f"Logger ver. {_version} | Log of module --> {self.name}\n")
            file.close()
            return True

        return result

    def add_note(self, line: str, add_date=True):
        with open(self.file_path, "a", encoding="utf-8") as file:
            file.write((f"{get_str_datetime(_time_format)} {line}" if add_date else line) + "\n")

    def printf(self, line: str):
        f_line = f"{get_str_datetime(_simple_time_format)} {line}"
        f_line_for_file = f"{get_str_datetime(_time_format)} {line}"
        print(f_line)
        self.add_note(line=f_line_for_file, add_date=False)

    def get_log(self) -> str:
        with open(self.file_path, "r", encoding="utf-8") as file:
            return file.readlines()