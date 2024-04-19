from disnake.ui import Modal, TextInput
from disnake import Embed, TextInputStyle


class SmartModal(Modal):
    def __init__(self, modal_cfg: dict):
        self.modal_cfg = modal_cfg
        super().__init__(title=modal_cfg["title"], custom_id=modal_cfg["custom_id"],
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