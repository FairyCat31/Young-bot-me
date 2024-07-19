import os
import sys
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


class Main:
    def __init__(self):
        # list of all req keys for program
        self.required_keys = [
            ("name_bot", "YoungMouse")
        ]
        # list of all opt keys for program
        self.optional_keys = [
        ]
        self.desc = self.__init_description()
        # create parser
        self.parser = self.__init_parser()
        # get args
        self.args = self.parser.parse_args()

    def __init_description(self) -> str:
        # Creating description, which print user, if user\'ll make mistake in setting keys
        description = "\nmain.py "
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
        parsed_args = vars(self.args)
        # init bot manager and init bot with args
        bman = bot_manager.BotManager()
        bman.init_bot(**parsed_args)
        bman.run_bot()
        return 0


if __name__ == "__main__":
    m = Main()
    m.main()
#     l = Logger("Test Module")
#     l.printf("Hello world!!!")
#     l.printf("simple warn -_-", type_message=TypeLogText.WARN)
#     l.printf("very critical error", type_message=TypeLogText.ERROR)
#     l.printf("some annoy warn", type_message=TypeLogText.WARN, log_text_in_file=False)
