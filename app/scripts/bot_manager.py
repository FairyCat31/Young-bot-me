import disnake
from disnake.ext import commands
from time import time
from dotenv import dotenv_values
from components.jsonmanager import JsonManager
from components.logger import Logger


class MEBot(commands.Bot):
    def __init__(self, name: str, cfg: JsonManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time()
        self.name = name
        self.cfg = cfg
        self.log = Logger(name=self.name, file_name=self.name)
        self.cfg.procedure_for_bots(self.name)

    def __repr__(self):
        return self.name

    async def on_ready(self):
        end_time = time()

        self.log.printf(self.cfg.replics["start"].format(user=self.user, during_time=end_time-self.start_time))


class BotManager():
    def __init__(self):
        self.cfg = JsonManager()
        self.log = Logger(name="Bot manager", file_name="bot_manager")
        self.cfg.dload_cfg(short_name="bots_properties.json")
        self.env_val = dotenv_values("data/sys/.env")
        self.BotsCont = {}
        self.log.printf("[&] Successful initialization of Bot manager")

    def init_assistant(func):
        def wrapper(self, name_bot):
            func(self,
                name_bot=name_bot,
                command_prefix=self.cfg.buffer[name_bot]["command_prefix"])

        return wrapper

    @init_assistant
    def init_bot(self, name_bot, **kwargs):
        self.log.printf(f"[&] Start to initialize a bot \"{name_bot}\"")
        intents = disnake.Intents.all()
        self.BotsCont[name_bot] = MEBot(name=name_bot, cfg=self.cfg, intents=intents, **kwargs)
        for cog in self.cfg.buffer[name_bot]["cogs"]:
            self.log.printf(f"[&] Import \"{cog}\" to bot \"{name_bot}\"")
            self.BotsCont[name_bot].load_extension(cog)
        token = self.env_val[f"{name_bot}_TOKEN"]
        self.log.printf(f"[&] Successful initialization of bot \"{name_bot}\"")
        self.log.printf(f"[&] Starting bot \"{name_bot}\"")
        self.BotsCont[name_bot].run(token)




