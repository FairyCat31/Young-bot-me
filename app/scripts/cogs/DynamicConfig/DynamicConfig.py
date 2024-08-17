from app.scripts.components.smartdisnake import MEBot
from app.scripts.cogs.DynamicConfig.DynamicConfigYoung import DynamicConfigYoung


CLASS_CONFIG_BY_NAME = {
    "YoungMouse": DynamicConfigYoung
}


def setup(bot: MEBot):
    dynamic_config_class = CLASS_CONFIG_BY_NAME.get(bot.name)
    if dynamic_config_class is None:
        raise ImportError(f"Can't found class config for bot {bot.name}")

    bot.add_cog(dynamic_config_class(bot))
