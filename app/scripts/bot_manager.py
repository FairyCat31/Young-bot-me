import disnake
from dotenv import dotenv_values
from components.jsonmanager import JsonManager, AddressType
from components.logger import Logger, TypeLogText
from components.smartdisnake import MEBot
from console_manager import Console
from multiprocessing import Process


class BotManager:
    def __init__(self):
        self.json_manager = JsonManager(AddressType.FILE, "bots_properties.json")
        self.json_manager.load_cfg()
        self.log = Logger(module_prefix="Bot Manager")
        self.env_val = dotenv_values("app/data/sys/.env")
        self.bot = None
        self.console = None
        self.log.printf("Successful initialization of Bot manager")

    @staticmethod
    def init_assistant(func):
        def wrapper(self, name_bot):
            buffer_bot_json = self.json_manager.get_buffer().get(name_bot)
            if not buffer_bot_json:
                self.log.printf(f"Can't find configuration parameters for bot \"{name_bot}\"",
                                type_message=TypeLogText.ERROR)
                exit(1)
            command_prefix = self.json_manager.get_buffer()[name_bot]["command_prefix"]
            func(self, name_bot=name_bot, command_prefix=command_prefix)

        return wrapper

    @init_assistant
    def init_bot(self, name_bot, **kwargs):
        self.log.printf(f"Start to initialize a bot \"{name_bot}\"")
        intents = disnake.Intents.all()
        self.bot = MEBot(name=name_bot, intents=intents, **kwargs)

        for cog in self.json_manager.get_buffer()[name_bot]["cogs"]:
            self.log.printf(f"Import \"{cog}\" to bot \"{name_bot}\"")
            self.bot.load_extension(cog)

        self.console = Console(self)
        self.log.printf(f"Successful initialization of bot \"{name_bot}\"")

    def run_bot(self):
        name_bot = self.bot.name
        token = self.env_val[f"{name_bot}_TOKEN"]
        self.log.printf(f"Starting bot \"{name_bot}\"")
        self.bot.run(token)
        # console_process = Process(target=self.console.start_handler)
        #
        # bot_process.start()
        # console_process.start()
        #
        # console_process.join()
        # bot_process.join()
