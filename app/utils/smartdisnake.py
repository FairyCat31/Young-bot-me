from typing import List, Dict, Coroutine
from time import time
import asyncio

from disnake import Embed, ButtonStyle
from disnake.ext import commands

from app.utils.ujson import JsonManager
from app.utils.logger import Logger


__pyfactory_package__ = {
    "name": "smartdisnake",
    "version": "1",
    "dependencies": {
        "logger": "1",
        "ujson": "1"
    }
}

BTN_STYLE_MAP = {
    1: ButtonStyle.primary,
    2: ButtonStyle.secondary,
    3: ButtonStyle.success,
    4: ButtonStyle.danger,
    5: ButtonStyle.success
}

# main class of bot
class SmartBot(commands.Bot):
    def __init__(self, name: str, **kwargs):
        super().__init__(intents=kwargs["intents"], command_prefix=kwargs["command_prefix"])
        self.start_time = time()
        self.name = name
        self._async_tasks_for_queue: List[Coroutine] = []
        self.props = JsonManager("bot_properties.json")
        self.props.load_from_file()
        self.log = Logger(name=name)
        self.async_sub_process_task = None

    def add_async_task(self, target: Coroutine) -> None:
        self._async_tasks_for_queue.append(target)

    async def start_async_tasks(self):
        await asyncio.gather(*self._async_tasks_for_queue)

    async def stop_async_tasks(self):
        if self.async_sub_process_task is not None:
            await asyncio.sleep(10)
            self.async_sub_process_task.cancel()

    async def on_ready(self):
        end_time = time()
        delta_time = ((end_time - self.start_time) // 0.0001) / 10000
        self.log.println(*self.props["def_phrases/start"]
                         .format(user=self.user, during_time=delta_time)
                         .split("\n"))
        self.async_sub_process_task = asyncio.create_task(self.start_async_tasks())
        await self.async_sub_process_task
        await self.stop_async_tasks()

    async def on_command_error(self,
                               context: commands.Context,
                               exception: commands.errors.CommandError) -> None:
        self.log.warn("Ignoring command -> %s" % context.message.content, log_text_in_file=False)


class SmartEmbed(Embed):
    def __init__(self, cfg: dict, dyn_vars: Dict[str, str]):
        self.dyn_vars = dyn_vars
        embed_funcs = {
            "thumbnail": super().set_thumbnail,
            "author": super().set_author,
            "footer": super().set_footer,
            "image": super().set_image
        }

        # create init args and super init
        init_args = {"color": cfg.get("color"), "url": cfg.get("url")}
        for arg in ("title", "description"):
            value = cfg.get(arg)
            if value is not None:
                value = value.format(**dyn_vars)
            init_args[arg] = value

        super().__init__(**init_args)

        # create fields and call init methods
        if cfg.get("fields") is not None:
            self.add_fields(cfg["fields"])

        for key in embed_funcs:
            if cfg.get(key) is None:
                continue
            embed_funcs[key](**cfg[key])

    def add_fields(self, embeds: List[dict]):
        for embed in embeds:
            super().add_field(name=embed["name"].format(**self.dyn_vars),
                              value=embed["value"].format(**self.dyn_vars),
                              inline=embed.get("inline"))
