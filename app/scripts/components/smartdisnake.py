from disnake.ui import Modal
from disnake import Embed, TextInput, TextInputStyle


class SmartModal(Modal):
    def __init__(self, cfg: dict):
        self.cfg = cfg
        super().__init__(title=cfg["title"], custom_id=cfg["custom_id"])
        super().components = [
            TextInput(
                label=ti["label"],
                placeholder=ti["placeholder"],
                max_length=ti["max_length"],
                min_length=ti["min_length"],
                required=ti["required"],
                custom_id=ti["custom_id"],
                style=TextInputStyle.long if ti["style"] == "long" else TextInputStyle.short
        ) for ti in cfg["text_inputs"]
        ]


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