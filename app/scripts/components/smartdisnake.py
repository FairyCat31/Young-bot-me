from disnake.ui import Modal, TextInput
from disnake.ext import commands
from disnake import Embed, TextInputStyle
from time import time
from app.scripts.components.logger import Logger, TypeLogText
from app.scripts.components.jsonmanager import JsonManagerForBots, AddressType


class MEBot(commands.Bot):

    def __init__(self, name: str, *args, **kwargs):
        self.start_time = time()
        super().__init__(*args, **kwargs)
        self.name = name
        self.json_manager = JsonManagerForBots(bot_name=name,
                                               type_address=AddressType.FILE,
                                               file_name_or_path="bots_properties.json")
        self.json_manager.load_cfg()
        self.log = Logger(module_prefix=name)

    def __repr__(self):
        return self.name

    async def on_ready(self):
        end_time = time()
        delta_time = end_time-self.start_time
        print(self.is_ready())
        self.log.printf(self.json_manager.bot_phrases["start"].format(user=self.user, during_time=delta_time))

    async def on_command_error(self, context: commands.Context, exception: commands.errors.CommandError) -> None:
        self.log.printf("Ignoring command -> %s" % context.message.content,
                        type_message=TypeLogText.WARN, log_text_in_file=False)


class SmartModal(Modal):
    def __init__(self, modal_cfg: dict):
        self.modal_cfg = modal_cfg
        super().__init__(title=modal_cfg["title"],
                         custom_id=modal_cfg["custom_id"],
                         components=[
                            TextInput(
                                label=ti["label"],
                                placeholder=ti["placeholder"],
                                max_length=ti["max_length"],
                                min_length=ti["min_length"],
                                required=ti["required"],
                                custom_id=ti["custom_id"],
                                style=TextInputStyle.long if ti["style"] == "long" else TextInputStyle.short
                            ) for ti in modal_cfg["text_inputs"]
                        ]
                         )


'''

{
    "part": int,
    "title": "str",
    "phrase_req_words": "Братик, напиши пожалуйста от {min_words} слов"
    "fields" :
    {         
            "question": "str 45 characters",
            "data_type": "str/int/(custom)",
            "custom_id": "str",
            "style": "long / short *optional"
            "min_words": "int *optional"
    }

}
            
'''


class SmartRegModal(Modal):
    def __init__(self, modal_cfg: dict):
        self.modal_cfg = modal_cfg
        super().__init__(
            title=self.modal_cfg["title"].format(part=int(modal_cfg["part"])),
            components=[
                TextInput(
                    label=field["question"],
                    placeholder=self.__get_placeholder(field),
                    max_length=3999,
                    min_length=0,
                    required=True,
                    custom_id=field["custom_id"],
                    style=TextInputStyle.long if field.get("style") == "long" else TextInputStyle.short
                ) for field in modal_cfg["fields"]
            ]

        )

    def __get_placeholder(self, field: dict) -> str:
        placeholder = "-"
        if not field.get("example") is None:
            return field["example"]
        if not field.get("min_words") is None:
            return self.modal_cfg["phrase_req_words"].format(min_words=field["min_words"])
        return placeholder


class SmartEmbed(Embed):
    def __init__(self, cfg: dict, **kwargs):
        super().__init__(
            title=cfg.get("title"),
            description=cfg.get("c"),
            **kwargs
        )
        for field in cfg["fields"]:
            super().add_field(
                name=field["name"],
                value=field["value"],
                inline=field["inline"],
            )
