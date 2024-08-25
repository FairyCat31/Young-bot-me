from disnake.ui import Modal, TextInput, Button, View
from typing import List, Dict
from disnake.ext import commands
from disnake import Embed, ButtonStyle
from time import time
from app.scripts.components.logger import Logger, LogType
from app.scripts.components.jsonmanager import JsonManager, AddressType

BTN_STYLE_MAP = {
    1: ButtonStyle.primary,
    2: ButtonStyle.secondary,
    3: ButtonStyle.success,
    4: ButtonStyle.danger,
    5: ButtonStyle.success
}


class MEBot(commands.Bot):

    def __init__(self, name: str, *args, **kwargs):
        self.start_time = time()
        super().__init__(*args, **kwargs)
        self.name = name
        self.props = JsonManager(AddressType.FILE, "bot_properties.json")
        self.props.load_from_file()
        self.log = Logger(module_prefix=name)

    def __repr__(self):
        return self.name

    async def on_ready(self):
        end_time = time()
        delta_time = end_time - self.start_time
        self.log.printf(self.props["phrases/start"].format(user=self.user, during_time=delta_time))

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
    def __init__(self, cfg: dict, **kwargs):
        map_args = {
            "thumbnail": super().set_thumbnail,
            "author": super().set_author,
            "footer": super().set_footer,
            "image": super().set_image,

        }
        args: Dict[str, str] = cfg["args"]
        func_args: List[dict] = cfg["func_args"]
        fields: List[Dict] = cfg["fields"]
        super().__init__(
            **args,
            **kwargs
        )
        for field in fields:
            super().add_field(**field)

        for func_arg in func_args:
            func = map_args[func_arg["func"]]
            args = func_arg["args"]
            func(**args)


class ButtonView(View):
    def __init__(self, buttons_group: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for button_parameters in buttons_group:
            button_parameters["style"] = BTN_STYLE_MAP[button_parameters["style"]]
            self.add_item(Button(**button_parameters))
