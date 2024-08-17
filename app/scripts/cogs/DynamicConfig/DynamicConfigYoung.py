from app.scripts.cogs.DynamicConfig.DynamicConfigShape import DynamicConfigShape
from app.scripts.components.jsonmanager import JsonManager, AddressType
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from typing import Any

# load choices for commands
CONFIG_FILE_NAME = "ym.json"
config_file: JsonManager = JsonManager(AddressType.FILE, CONFIG_FILE_NAME)
config_file.load_from_file()
CHOICES_FROM_FILE = list(config_file.get_buffer().keys())
CHOICES_TO_RESET = CHOICES_FROM_FILE.copy()
CHOICES_TO_RESET.append("ALL")


class DynamicConfigYoung(DynamicConfigShape):
    @commands.slash_command(description="Задать новое значение параметру", name="config_set_param")
    @commands.default_member_permissions(administrator=True)
    async def config_set_param(self, inter: ApplicationCommandInteraction,
                               parameter: str = commands.Param(choices=CHOICES_FROM_FILE),
                               value: Any = None):
        await super().config_set_param(self, inter, parameter, value)

    @commands.slash_command(description="Показать текущие настройки", name="config_reset")
    @commands.default_member_permissions(administrator=True)
    async def config_reset(self, inter: ApplicationCommandInteraction,
                           parameter: str = commands.Param(choices=CHOICES_TO_RESET)):
        await super().config_reset(self, inter, parameter)
