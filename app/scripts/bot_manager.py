from utils.logger import Logger, PrintHandler, ErrorHandler
from utils.ujson import JsonManager, AddressType
from utils.smartdisnake import SmartBot
from dotenv import dotenv_values
from disnake import Intents
import sys


class BotManager:
    def __init__(self, debug_mode: bool = True, advanced_logging: bool = True):
        # init logger and redirect standard err and out streams to logger
        self.log = Logger(name="Bot Manager", debug_mode=debug_mode)
        self._debug_mode = debug_mode
        if advanced_logging:
            sys.stderr = ErrorHandler(self.log)
            sys.stdout = PrintHandler(self.log)
        self.json_manager = JsonManager(AddressType.FILE, "bot_properties.json")
        self.bot_man_props = JsonManager(AddressType.FILE, "factory.json")
        self.json_manager.load_from_file()
        self.bot_man_props.load_from_file()
        self.__env_val = dotenv_values(self.bot_man_props[".env"])
        self.bot = None
        self.log.printf(self.bot_man_props["init_bm"])

    def init_bot(self, **kwargs):
        command_prefix = self.json_manager["command_prefix"]
        self.log.printf(self.bot_man_props["init_bot"])
        intents = Intents.all()
        self.bot = SmartBot(intents=intents, command_prefix=command_prefix, **kwargs)
        self.bot.log.debug_mode = self._debug_mode
        for cog in self.json_manager["cogs"]:
            self.log.printf(self.bot_man_props["import_cog"].format(cog=cog))
            self.bot.load_extension(cog)

        self.log.printf(self.bot_man_props["init_successful_bot"])

    def run_bot(self):
        token = self.__env_val["BOT_TOKEN"]
        self.log.printf(self.bot_man_props["st_bot"])
        self.bot.run(token)
