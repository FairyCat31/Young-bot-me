from typing import Any
from app.scripts.cogs.DynamicConfig.DynamicConfigShape import DynamicConfigShape
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from app.scripts.components.jsonmanager import JsonManager, AddressType


CONFIG_FILE_NAME = "ym.json"
config_file = JsonManager(AddressType.FILE, CONFIG_FILE_NAME)
config_file.load_cfg()
CHOICES_FROM_FILE = list(config_file.get_buffer().keys())


class DynamicConfigYoung(DynamicConfigShape):

    @commands.slash_command(description="Задать новое значение параметру", name="config_set_param")
    @commands.default_member_permissions(administrator=True)
    async def config_set_param(self, inter: ApplicationCommandInteraction,
                               parameter: str = commands.Param(choices=CHOICES_FROM_FILE),
                               value: Any = None):
        await super().config_set_param(self, inter, parameter, value)
