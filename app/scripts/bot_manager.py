import datetime
import disnake
from dotenv import dotenv_values
from components.jsonmanager import JsonManager, AddressType
from components.logger import Logger, LogType
from components.smartdisnake import MEBot
# from console_manager import Console


class BotManager:
    def __init__(self):
        self.json_manager = JsonManager(AddressType.FILE, "bot_properties.json")
        self.json_manager.load_from_file()
        self.log = Logger(module_prefix="Bot Manager")
        self.env_val = dotenv_values("app/data/sys/.env")
        self.bot = None
        self.is_alive = True
        self.log.printf("Successful initialization of Bot manager")
        self.optional_prepare_func_map = {
            "activity": self.__get_activity,
            "created_at": self.__get_start_time
        }

    @staticmethod
    def __get_start_time() -> datetime.datetime:
        return datetime.datetime.now()

    @staticmethod
    def __get_activity(args: dict) -> disnake.Activity:
        activity_type = {
            "game": disnake.ActivityType.playing,
            "listening": disnake.ActivityType.listening,
            "streaming": disnake.ActivityType.streaming
        }
        args["type"] = activity_type[args["type"]]
        activity = disnake.Activity(**args)
        return activity

    def init_bot(self, name_bot, **kwargs):
        for key in kwargs.keys():
            convert_func = self.optional_prepare_func_map.get(key)
            if convert_func is None:
                continue

            kwargs[key] = convert_func(kwargs[key])
        command_prefix = self.json_manager["command_prefix"]
        self.log.printf(f"Start to initialize a bot \"{name_bot}\"")
        intents = disnake.Intents.all()
        self.bot = MEBot(name=name_bot, intents=intents, command_prefix=command_prefix, **kwargs)

        for cog in self.json_manager["cogs"]:
            self.log.printf(f"Import \"{cog}\" to bot \"{name_bot}\"")
            self.bot.load_extension(cog)

        self.log.printf(f"Successful initialization of bot \"{name_bot}\"")

    def run_bot(self):
        name_bot = self.bot.name
        token = self.env_val[f"{name_bot}_TOKEN"]
        self.log.printf(f"Starting bot \"{name_bot}\"")
        self.bot.run(token)
