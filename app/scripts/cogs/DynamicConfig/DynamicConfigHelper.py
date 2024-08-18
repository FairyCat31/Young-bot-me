"""
useful tools for using DynamicConfig in other cogs
"""
from disnake import MessageInteraction
from app.scripts.components.logger import LogType


def is_cfg_setup(cfg: dict, *parameters) -> str:
    output = ""
    for par in parameters:
        if cfg[par] is None:
            output = par
            break

    return output
