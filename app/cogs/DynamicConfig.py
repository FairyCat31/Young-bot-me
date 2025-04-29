from typing import Any, List, Dict, Callable
from functools import wraps as wrapper_func

from disnake import ApplicationCommandInteraction, Role, Interaction
from disnake.ext import commands

from app.utils.logger import LogType
from app.utils.ujson import JsonManager
from app.utils.smartdisnake import SmartBot


__pyfactory_package__ = {
    "name": "dynamic_config",
    "version": "1.0",
    "dependencies": {
        "smartdisnake": "1",
        "ujson": "1"
    }
}

# subclass for the Dynamic Config Shape
class ValueConvertor:
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
            "ROLE": self._convert_discord_role_to_discord_id,
            "DC_OBJ": self._convert_discord_obj_to_discord_id,
            "TEXT_CHANNEL": self._convert_discord_obj_to_discord_id
        }
        convert_func = self.convert_func_by_type.get(self._value_type)
        if convert_func is not None:
            self._convert_value = convert_func(self._original_value)

    @property
    def convert_value(self) -> Any:
        return self._convert_value

    # convert methods

    @staticmethod
    def _convert_str_to_bool(line: str) -> bool:
        return line.lower() in ["true", "1", "yes", "y"]

    @staticmethod
    def _convert_discord_obj_to_discord_id(line: str) -> int | None:
        if len(line) < 4:
            return

        ds_id = line[2:-1]
        if not ds_id.isdigit():
            return

        return int(ds_id)

    @staticmethod
    def _convert_discord_role_to_discord_id(line: str) -> int | None:
        if len(line) < 5:
            return

        ds_id = line[2:-1]
        if not ds_id.isdigit():
            return

        return int(ds_id)


class DynamicConfigCog(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot
        file_name = bot.props["dynamic_config_file_name"]
        self.dynamic_json = JsonManager(file_name)
        self.dynamic_json.load_from_file()

    @staticmethod
    def is_cfg_setup(*params: str, echo: bool = True, discord_response: bool = False):
        """
        Check if dyn params is set and cancel func if it not

        Args:
            *params: list of dyn vars for the checking
            echo: console logging
            discord_response: chat logging to user
        """
        def decorator(function):
            @wrapper_func(function)
            async def wrapper(self, *args, **kwargs):
                output = ""
                for par in params:
                    if self.bot.props[f"dynamic_config/{par}"] is None:
                        output = par
                        break
                if not output:
                    await function(self, *args, **kwargs)
                    return
                output = self.bot.props["def_phrases/RunErrorDynConfig"] % output
                if echo:
                    self.bot.log.printf(output, LogType.WARN)
                if discord_response:
                    inter = kwargs.get("inter")
                    if inter is None or not issubclass(type(inter), Interaction):
                        if len(args) > 0:
                            inter = args[0]
                    if inter is None or not issubclass(type(inter), Interaction):
                        print("Ошибка отработки is_cfg_setup")
                        return
                    await inter.response.send_message(output)
                return
            return wrapper
        return decorator

    @staticmethod
    def has_any_roles(*role_tags: str, discord_response: bool = True):
        """
        check roles exist by dyn vars

        Args:
            *role_tags: dyn vars name
            discord_response: chat logging to user

        """
        def decorator(func: Callable):
            @wrapper_func(func)
            async def wrapper(self, *args, **kwargs) -> Any:
                role_ids = [self.bot.props[f"dynamic_config/{role_tag}"] for role_tag in role_tags]
                inter: ApplicationCommandInteraction = kwargs["inter"]
                member_roles: List[Role] = inter.author.roles
                member_role_ids = [role.id for role in member_roles]
                for role_id in role_ids:
                    if role_id in member_role_ids:
                        continue
                    if discord_response:
                        await inter.response.send_message(self.bot.props["def_phrases/PermErrorDynConfig"])
                    else:
                        await inter.response.defer()
                    return
                result = await func(self, *args, **kwargs)
                return result
            return wrapper
        return decorator

    # load config from file
    def _load_dynamic_config(self) -> Dict[str, Any]:
        dyn_buffer = self.dynamic_json.buffer
        dynamic_config = {}
        for key in dyn_buffer.keys():
            dynamic_config[key] = self.dynamic_json[f"{key}/value"]
        return dynamic_config.copy()

    # reload values
    def _reload_dynamic_config(self):
        self.dynamic_json.write_in_file()
        self.bot.props["dynamic_config"] = self._load_dynamic_config()

    def _gen_value_table(self) -> str:
        """
        Generate beautiful table for printing

        """
        dynamic_config = self._load_dynamic_config()
        len_key_column = max(map(len, dynamic_config.keys()))
        len_value_column = max(map(lambda v: len(str(v)), dynamic_config.values()))
        line_format = "{:<%i} {:<%i}" % (len_key_column + 5, len_value_column + 5)
        result = line_format.format('parameter', 'value') + "\n"
        lines = [line_format.format(key, str(value)) for key, value in dynamic_config.items()]
        result += "```" + "\n".join(lines) + "```"
        return result


    async def config_set_param(self, inter: ApplicationCommandInteraction, parameter: str, value: Any) :
        """
        Slash command for the setting value

        """

        data_type_need = self.dynamic_json[f"{parameter}/type"]
        convert_value = ValueConvertor(data_type_need, value).convert_value

        if convert_value is None:
            await inter.response.send_message(
                self.bot.props["def_phrases/FormatErrorDynConfig"]
            .format(value=value, data_type_need=data_type_need)
            )
            self.bot.log.printf(self.bot.props["def_phrases/ConsoleFormatErrorDynConfig"], log_type=LogType.WARN)
            return

        self.dynamic_json[f"{parameter}/value"] = convert_value
        self._reload_dynamic_config()

        await inter.response.send_message(self._gen_value_table())
        print(self.bot.props["def_phrases/ConsoleEditInfo"]
                            .format(parameter=parameter, convert_value=value))

    async def config_show(self, inter: ApplicationCommandInteraction):
        """
        Print all params in discord

        """

        await inter.response.send_message(self._gen_value_table())

    async def config_reset(self, inter: ApplicationCommandInteraction, parameter: str = ""):
        """
        Reset value of dyn var


        """

        if parameter != "ALL":
            self.dynamic_json[f"{parameter}/value"] = None
        else:
            var_names = self.dynamic_json.keys()
            for var_name in var_names:
                self.dynamic_json[f"{var_name}/value"] = None

        self._reload_dynamic_config()

        await inter.response.send_message(self._gen_value_table())

# method for building class with data from bot_properties
def build(bot: SmartBot):
    file_name = bot.props["dynamic_config_file_name"]
    cfg_file = JsonManager(file_name)
    cfg_file.load_from_file()
    chs_to_set_param = list(cfg_file.keys())
    chs_to_del_param = chs_to_set_param.copy()
    chs_to_del_param.append("ALL")

    class BuildDynamicConfig(DynamicConfigCog):
        # bind decorators from properties

        @commands.slash_command(**bot.props["cmds/main_cfg"])
        @commands.default_member_permissions(administrator=True)
        async def config(self, inter):
            pass

        @config.sub_command(**bot.props["cmds/set_cfg"])
        async def config_set(self, inter: ApplicationCommandInteraction,
                             parameter: str = commands.Param(choices=chs_to_set_param),
                             value: str = None):
            await super().config_set_param(inter, parameter, value)

        @config.sub_command(**bot.props["cmds/show_cfg"])
        async def config_show(self, inter):
            await super().config_show(inter)

        @config.sub_command(**bot.props["cmds/del_cfg"])
        async def config_reset(self, inter,
                               parameter: str = commands.Param(choices=chs_to_del_param)):
            await super().config_reset(inter, parameter)

    return BuildDynamicConfig


def setup(bot: SmartBot):
    build_class = build(bot)
    bot.add_cog(build_class(bot))
