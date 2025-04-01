import asyncio
from disnake.ui import Modal, TextInput, Button, View
from typing import List, Dict
from disnake.ext import commands
from disnake import Embed, ButtonStyle
from time import time
from app.scripts.utils.logger import Logger, LogType
from app.scripts.utils.ujson import JsonManager, AddressType
from typing import Coroutine


BTN_STYLE_MAP = {
    1: ButtonStyle.primary,
    2: ButtonStyle.secondary,
    3: ButtonStyle.success,
    4: ButtonStyle.danger,
    5: ButtonStyle.success
}


class SmartBot(commands.Bot):
    def __init__(self, name: str, **kwargs):
        self.start_time = time()
        super().__init__(intents=kwargs["intents"], command_prefix=kwargs["command_prefix"])
        self.name = name
        self._async_tasks_for_queue = []
        self.props = JsonManager(AddressType.FILE, "bot_properties.json")
        self.props.load_from_file()
        self.log = Logger(name=name)

    def add_async_task(self, target: Coroutine) -> None:
        self._async_tasks_for_queue.append(target)

    async def start_async_tasks(self):
        await asyncio.gather(*self._async_tasks_for_queue)

    async def on_ready(self):
        end_time = time()
        delta_time = end_time - self.start_time
        self.log.println(*self.props["def_phrases/start"].format(user=self.user, during_time=delta_time).split("\n"))
        await asyncio.create_task(self.start_async_tasks())

    async def on_command_error(self, context: commands.Context, exception: commands.errors.CommandError) -> None:
        self.log.printf("Ignoring command -> %s" % context.message.content,
                        log_type=LogType.WARN, log_text_in_file=False)


class SmartModal(Modal):
    def __init__(self, cfg: dict):
        modal_args: dict = cfg["args"]
        fields: List[dict] = cfg["fields"]
        text_inputs: list = []
        for field in fields.copy():
            field.setdefault("required", True)
            field.setdefault("max_length", 1024)
            text_inputs.append(TextInput(**field))

        super().__init__(**modal_args, components=text_inputs)


class SmartRegModal(Modal):
    def __init__(self, sett: dict, modal_id: int):
        self.modal_id = modal_id
        title: str = sett["title"].format(part=modal_id)
        custom_id: str = f"reg_modal_{modal_id}"
        self.questions_sett = None
        questions, self.questions_sett = self.__init_questions(sett)
        super().__init__(title=title, custom_id=custom_id, components=questions)

    @staticmethod
    def __init_questions(sett: dict) -> (List[TextInput], List[dict]):
        questions = []
        phrase_req_words: str = sett["phrase_req_words"]
        questions_sett: List[Dict[str, dict]] = sett["questions"]
        map_args = {
            "min_words": lambda x: ("placeholder", phrase_req_words.format(min_words=x)),
            "example": lambda x: ("placeholder", x)
        }
        for question_sett in questions_sett:
            args = question_sett["classic"].copy()
            question_sett.setdefault("custom", {})
            for func_name, func_arg in question_sett["custom"].items():
                k, v = map_args[func_name](func_arg)
                args[k] = v

            questions.append(TextInput(**args))

        return questions, questions_sett


class SmartEmbed(Embed):
    def __init__(self, cfg: dict, dyn_vars: Dict[str, str]):
        self.dyn_vars = dyn_vars
        embed_funcs = {
            "thumbnail": super().set_thumbnail,
            "author": super().set_author,
            "footer": super().set_footer,
            "image": super().set_image
        }

        init_args = {"color": cfg.get("color"), "url": cfg.get("url")}
        for arg in ["title", "description"]:
            value: str = cfg.get(arg)
            if value is not None:
                value = value.format(**dyn_vars)
            init_args[arg] = value


        super().__init__(**init_args)

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


class ButtonView(View):
    def __init__(self, buttons_group: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for button_parameters in buttons_group:
            button_parameters["style"] = BTN_STYLE_MAP[button_parameters["style"]]
            self.add_item(Button(**button_parameters))
