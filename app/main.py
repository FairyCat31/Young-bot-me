from utils.ujson import JsonManagerWithCrypt
from factory.errors import FactoryStartArgumentError
from sys import argv as sys_argv
from json5 import loads
from json import dumps
from typing import Any
from bot_manager import BotManager


__all__ = [
    "Main"
]
"""
0 - all ok
1 - unknown arg format
2 - func arg set earlier than func
3 - args not set
4 - unknown procedure
"""
__pyfactory_package__ = {
    "name": "main",
    "version": "1.0",
    "dependencies": {
        "bot_manager": "1"
    }
}


class ArgParser:
    def __init__(self):
        self.func_count = -1
        self.error_arg = ""
        self.code = 0

    # convert sub argument value to right data type
    @staticmethod
    def __convert_sub_arg(value: str) -> Any:

        if value.isdigit():
            return int(value)
        elif value.replace('.', '', 1).isdigit():
            return float(value)
        elif value[0] == "[" or value[0] == "{":
            print(value)
            return loads(value)
        elif value.lower() in ["true", "yes", "y"]:
            return True
        elif value.lower() in ["false", "no", "n"]:
            return False
        return value

    def parse_args(self, main_obj, procs_obj) -> int:
        # start parsing

        len_args = len(sys_argv)
        # check if set args
        if len_args == 1:
            self.code = 3

        for i in range(1, len_args):
            arg = sys_argv[i]
            # check is correct format
            if arg[0] != "-":
                self.code = 1
                self.error_arg = arg
                break

            if arg[1] == "-":
                if self.func_count == -1:
                    self.error_arg = arg
                    self.code = 2
                    break
                pd_arg = arg.split("=")
                main_obj.func_args[self.func_count][pd_arg[0][2:]] = self.__convert_sub_arg(pd_arg[1])

            else:
                self.func_count += 1
                main_obj.func_args.append({})
                try:
                    main_obj.start_func.append(getattr(procs_obj, arg[1:]))
                except AttributeError:
                    self.error_arg = arg
                    self.code = 4
                    break

        return self.code


class StartProcedures:

    @staticmethod
    def h():
        """-h - Print information about arg and usage"""
        return StartProcedures.help()

    @staticmethod
    def help():
        """-help - Print information about arg and usage"""
        out = "Py Factory\nusage: main.py -option --parameter=value\nOptions:\n"
        out += "\n".join([func.__doc__ for func in StartProcedures.__dict__.values() if type(func) == staticmethod])
        print(out)

    @staticmethod
    def launch_bot(**kwargs):
        """-launch_bot - Launch bot
        --name | str
        --debug_mode | bool (Optional)
        --advanced_logging | bool (Optional)"""
        debug_mode = kwargs.get("debug_mode")
        advanced_logging = kwargs.get("advanced_logging")
        if debug_mode is None: debug_mode = False
        if advanced_logging is None: advanced_logging = False

        bm = BotManager(debug_mode=debug_mode, advanced_logging=advanced_logging)
        bm.init_bot(**kwargs)
        bm.run_bot()

    @staticmethod
    def add_db(db_data: dict):
        """-add_db - Add connection data
        --db_data | dict"""
        jsm = JsonManagerWithCrypt(".dbs.crptjson")
        jsm.load_from_file()
        for name, data in db_data.items():
            jsm[name] = data
        jsm.write_in_file()

    @staticmethod
    def show_db(name: str = ""):
        """-show_db - Print data for the db connection
        --name: | str (Optional)"""
        jsm = JsonManagerWithCrypt(".dbs.crptjson")
        jsm.load_from_file()
        if name:
            print(dumps(jsm[name], indent=2))
        else:
            print(dumps(jsm.buffer, indent=2))

    @staticmethod
    def del_db(name: str = ""):
        """-del_db - Del data for the db connection
        --name: | str (Optional)"""
        jsm = JsonManagerWithCrypt(".dbs.crptjson")
        jsm.load_from_file()
        b = jsm.buffer
        if name:
            del b[name]
        else:
            b = {}
        jsm.buffer = b
        jsm.write_in_file()

    @staticmethod
    def add_serv(serv_data: dict):
        """-add_serv - Print data for the rcon connection
        --serv_data: | dict"""
        jsm = JsonManagerWithCrypt(".rcon_servers.crptjson")
        jsm.load_from_file()
        for name, data in serv_data.items():
            jsm[name] = data
        jsm.write_in_file()

    @staticmethod
    def show_serv(name: str = ""):
        """-show_serv - Show data for the rcon connection
        --name: | str (Optional)"""
        jsm = JsonManagerWithCrypt(".rcon_servers.crptjson")
        jsm.load_from_file()
        if name:
            print(dumps(jsm[name], indent=2))
        else:
            print(dumps(jsm.buffer, indent=2))

    @staticmethod
    def del_serv(name: str = ""):
        """-del_serv - Del data for the rcon connection
        --name: | str (Optional)"""
        jsm = JsonManagerWithCrypt(".rcon_servers.crptjson")
        jsm.load_from_file()
        b = jsm.buffer
        if name:
            del b[name]
        else:
            b = {}
        jsm.buffer = b
        jsm.write_in_file()

class Main:
    def __init__(self):
        self.start_func = []
        self.func_args = []

    def main(self):
        arg_parser = ArgParser()
        arg_parser.parse_args(self, StartProcedures)
        if arg_parser.code:
            raise FactoryStartArgumentError(arg_parser.code, arg_parser.error_arg)
        for i in range(len(self.func_args)):
            self.start_func[i](**self.func_args[i])


if __name__ == "__main__":
    m = Main()
    m.main()