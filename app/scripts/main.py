import sys
import os
from json import loads
import argparse
sys.path.insert(1, os.path.join(sys.path[0].replace("/app/scripts", "")))
import bot_manager


__all__ = [
    "Main"
]


# create children class with edit error message
class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        self.description = kwargs["description"]
        super().__init__(*args, **kwargs)

    def error(self, message):

        self.exit(2, '%s\n\n\nERROR: %s\n' % (self.description, message))

    def parse_args(self, *args, **kwargs):
        dict_args = vars(super().parse_args(*args, **kwargs))

        all_keys = tuple(dict_args.keys())

        for key in all_keys:

            if dict_args[key] is None:
                del dict_args[key]
                continue

            if type(dict_args[key]) is not str:
                continue

            first_symbol = dict_args[key][0]
            if first_symbol == "{" or first_symbol == "[":
                dict_args[key] = loads(dict_args[key])
                continue

        return dict_args


class Main:
    def __init__(self):
        # list of all req keys for program
        self.required_keys = [
            ("name_bot", "YoungMouse")
        ]
        # list of all opt keys for program
        self.optional_keys = [
            ("activity", "{'name': 'unimice.ru', 'type': 'game'}")
        ]
        self.desc = self.__init_description()
        # create parser
        self.parser = self.__init_parser()
        # get args
        self.args = self.parser.parse_args()

    def __init_description(self) -> str:
        # Creating description, which print user, if user\'ll make mistake in setting keys
        description = "\ndbmanager.py "
        # generate str and plus with desc
        # format: -name <name:str> -old <12:int>
        description += " ".join(["-%s <%s:%s>" % (k, e, type(e)) for k, e in self.required_keys])

        """
        if optional_keys tuple is not empty

        generate str and plus with desc
        format:

        optional arguments:
            -sub <test:str>
            -debug
        """
        description += "\n\noptional arguments:\n\t-h"
        if self.optional_keys:

            description += "\n\t" + "\n\t".join(
                ["-%s <%s:%s>" % (k, e, type(e)) if e else "-%s" % k for k, e in self.optional_keys]
            )

        return description

    def __init_parser(self) -> ArgumentParser:

        # init parser with desc
        parser = ArgumentParser(description=self.desc, add_help=False)
        # init args from required_keys and optional_keys
        for args in self.required_keys:
            k, t = args
            parser.add_argument(f"-{k}",
                                type=type(t),
                                required=True)
        for args in self.optional_keys:
            k, t = args
            parser.add_argument(f"-{k}",
                                type=type(t))

        return parser

    def main(self) -> int:
        # convert object field to dict
        print("\n\n\\|/ Bot constructor 0.3 alpha \\|/\n\n+ start of list args\n|\n|- " +
              "\n|- ".join(f"{key}={value}" for key, value in self.args.items()) + "\n|\n+ end of list args\n")
        # init bot manager and init bot with args
        bman = bot_manager.BotManager()
        bman.init_bot(**self.args)
        bman.run_bot()
        return 0


if __name__ == "__main__":
    m = Main()
    m.main()
