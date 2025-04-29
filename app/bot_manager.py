import sys

from dotenv import dotenv_values
from disnake import Intents

from utils.logger import Logger, PrintHandler, ErrorHandler
from utils.ujson import JsonManager
from utils.smartdisnake import SmartBot


__pyfactory_package__ = {
    "name": "bot_manager",
    "version": "1.0",
    "dependencies": {
        "smartdisnake": "1",
        "bot_properties": "1"
    }
}

class BotManager:
    def __init__(self, debug_mode: bool = True, advanced_logging: bool = True):
        self.bot: SmartBot | None = None

        # init logger and redirect standard err and out streams to logger
        self.log = Logger(name="Bot Manager", debug_mode=debug_mode)
        self._debug_mode = debug_mode
        if advanced_logging:
            sys.stderr = ErrorHandler(self.log)
            sys.stdout = PrintHandler(self.log)

        # load json files
        self.bot_properties = JsonManager("bot_properties.json")
        self.factory_jsm = JsonManager("factory.json")
        self.bot_properties.load_from_file()
        self.factory_jsm.load_from_file()
        self.__env_val = dotenv_values(self.factory_jsm[".env"])

        self.log.printf(self.factory_jsm["init_bm"])

    def init_bot(self, **kwargs):
        self.log.printf(self.factory_jsm["init_bot"])

        command_prefix = self.bot_properties["command_prefix"]
        intents = Intents.all()
        self.bot = SmartBot(intents=intents, command_prefix=command_prefix, **kwargs)
        self.bot.log.debug_mode = self._debug_mode
        for cog in self.bot_properties["cogs"]:
            self.log.printf(self.factory_jsm["import_cog"].format(cog=cog))
            self.bot.load_extension(cog)

        self.log.printf(self.factory_jsm["init_successful_bot"])

    def run_bot(self):
        token = self.__env_val["BOT_TOKEN"]
        self.log.printf(self.factory_jsm["st_bot"])
        self.bot.run(token)
        print("гооооооооол")

    #def stop_bot
