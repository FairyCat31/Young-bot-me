import disnake
from disnake.ext import commands
from time import time
from dotenv import dotenv_values
from components.jsonmanager import JsonManager


class MEBot(commands.Bot):
    def __init__(self, name: str, cfg: JsonManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time()
        self.name = name
        self.cfg = cfg
        self.cfg.procedure_for_bots(self.name)

    def __repr__(self):
        return self.name

    async def on_ready(self):
        end_time = time()

        print(self.cfg.replics["start"].format(user=self.user, during_time=end_time-self.start_time)) # "Successful starting\\nI logged as {user}\\nStarting during: {du}"


class BotManager():
    def __init__(self):
        self.cfg = JsonManager()
        self.cfg.dload_cfg(short_name="bots_properties.json")
        self.env_val = dotenv_values("data/sys/.env")
        self.BotsCont = {}

    def init_assistant(func):
        def wrapper(self, name_bot):
           func(self,
               name_bot=name_bot,
               command_prefix=self.cfg.buffer[name_bot]["command_prefix"])

        return wrapper

    @init_assistant
    def init_bot(self, name_bot, **kwargs):
        intents = disnake.Intents.all()
        self.BotsCont[name_bot] = MEBot(name=name_bot, cfg=self.cfg, intents=intents, **kwargs)
        for cog in self.cfg.buffer[name_bot]["cogs"]:
            self.BotsCont[name_bot].load_extension(cog)
            print("import " + cog)
        token = self.env_val[f"{name_bot}_TOKEN"]
        self.BotsCont[name_bot].run(token)


bman = BotManager()
bman.init_bot(name_bot="YoungMouse")

