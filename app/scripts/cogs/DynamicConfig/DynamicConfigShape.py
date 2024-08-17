from typing import Any
from app.scripts.components.logger import LogType
from disnake.ext import commands
from disnake.abc import Snowflake
from disnake import ApplicationCommandInteraction
from app.scripts.components.jsonmanager import JsonManager, AddressType
from app.scripts.components.smartdisnake import MEBot
from typing import Optional


class ValueConvertorFromUser:
    def __init__(self, value_type: str, value: str):
        self._value_type = value_type
        self._original_value = value
        self._convert_value = None
        self.convert_func_by_type = {
            "STR": str,
            "FLOAT": float,
            "INT": int,
            "BOOL": self._convert_str_to_bool,
            "USER": self._convert_discord_obj_to_discord_id,
            "ROLE": self._convert_discord_obj_to_discord_id,
            "DC_OBJ": self._convert_discord_obj_to_discord_id,
            "TEXT_CHANNEL": self._convert_discord_obj_to_discord_id
        }
        convert_func = self.convert_func_by_type.get(self._value_type)
        if convert_func is not None:
            try:
                self._convert_value = convert_func(self._original_value)
            except AttributeError:
                self._convert_value = None
            except ValueError:
                self._convert_value = None

    @staticmethod
    def _convert_str_to_bool(line: str) -> bool:
        return line.lower() in ["true", "1", "yes", "y"]

    @staticmethod
    def _convert_discord_obj_to_discord_id(line: str) -> int:
        return int(line[2:-1])

    def return_convert_value(self):
        return self._convert_value


class DynamicConfigShape(commands.Cog):
    def __init__(self, bot: MEBot):
        self.bot = bot
        file_name = bot.json_manager.get_bot_properties()["dynamic_config_file_name"]
        self.dynamic_json = JsonManager(address_type=AddressType.FILE, file_name_or_path=file_name)
        self.dynamic_json.load_from_file()
        self.__update_dynamic_config__()

    """
        convert and get dyn conf
        from
        { par:
            {value: test, type: str}
        }
        to
        {par: test}
        """
    def __get_dynamic_config__(self) -> dict[str, Any]:
        dyn_buffer = self.dynamic_json.get_buffer()
        dynamic_config = {}
        for key in dyn_buffer.keys():
            dynamic_config[key] = dyn_buffer[key]["value"]
        return dynamic_config

    # update parameter "dynamic_config" in bot's buffer of json_manager
    def __update_dynamic_config__(self) -> None:
        new_bot_properties = self.bot.json_manager.get_bot_properties()
        new_bot_properties["dynamic_config"] = self.__get_dynamic_config__()
        self.bot.json_manager.set_bot_properties(new_bot_properties)
        self.dynamic_json.write_in_file()

    @commands.slash_command(description="Задать новое значение параметру", name="config_setup")
    @commands.default_member_permissions(administrator=True)
    async def config_set_param(self, inter: ApplicationCommandInteraction,
                               parameter,
                               value):
        # data type which set in config
        data_type_need = self.dynamic_json[f"{parameter}/type"]
        # data type of value which took user
        convert_value = ValueConvertorFromUser(data_type_need, value).return_convert_value()
        if convert_value is None:
            await inter.response.send_message(
                f"Ошибка обновления параметра.\nНеудалось преобразовать {value} в {data_type_need}")
            self.bot.log.printf("IncorrectTypeParameter: Failed to update parameter value", log_type=LogType.WARN)
            return
        # if all ok we get response what all ok
        await inter.response.send_message(f"Параметр изменён\n{parameter} ---> {convert_value}")
        self.dynamic_json[f"{parameter}/value"] = convert_value

        # update new config in bot json_manager
        self.__update_dynamic_config__()
        # log what all ok
        self.bot.log.printf(f"Параметр {parameter} изменён ---> {convert_value}")

    # print all params in discord
    @commands.slash_command(description="Показать текущие настройки")
    @commands.default_member_permissions(administrator=True)
    async def config_show(self, inter: ApplicationCommandInteraction):
        sett = self.bot.json_manager.get_bot_properties()["dynamic_config"]
        message = ""
        for key, value in sett.items():
            message += f"\n{key} ---> {value}"
        await inter.response.send_message(message)

    @commands.slash_command(description="Показать текущие настройки")
    @commands.default_member_permissions(administrator=True)
    async def config_reset(self, inter: ApplicationCommandInteraction, parameter: Optional[str] = ""):
        if parameter != "ALL":
            self.dynamic_json[f"{parameter}/value"] = None
            self.__update_dynamic_config__()
            await inter.response.send_message(f"Параметр изменён\n{parameter} ---> None")
            return

        buffer = self.dynamic_json.get_buffer()
        parameters = buffer.keys()
        for parameter in parameters:
            self.dynamic_json[f"{parameter}/value"] = None
        self.__update_dynamic_config__()
        await inter.response.send_message("Все параметры сброшены")