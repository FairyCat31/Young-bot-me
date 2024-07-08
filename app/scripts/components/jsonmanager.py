from json import dump, load
from typing import Dict, Any

PATH_CONFIG_JSON = "data/json/json_conf.json"


class JsonManager:
    def __init__(self, is_not_path: bool, file_name_or_path: str):
        """
        load config for working JsonManager

        default_path
        indent
        encoding
        """
        with open(PATH_CONFIG_JSON, "r") as f:
            self.json_config = load(f)

        # set path and name file
        if is_not_path:
            self._name = file_name_or_path
            self._path = self.json_config["path_to_json_files"] + self._name
        else:
            self._path = file_name_or_path
            self._name = self._path.split("/")[-1]
        # create dict which will content all data from file.json
        self._buffer = {}

    def __str__(self):
        return str(self._buffer)

    def load_cfg(self) -> None:
        with open(self._path, "r", encoding=self.json_config["encoding"]) as f:
            self._buffer = load(f)

    def write_cfg(self) -> None:
        with open(self._path, "w", encoding=self.json_config["encoding"]) as f:
            dump(self._buffer, f, indent=self.json_config["indent"])

    def get_buffer(self) -> dict[str, Any]:
        return self._buffer

    def set_buffer(self, dictionary: dict) -> None:
        self._buffer = dictionary


class JsonManagerForBots(JsonManager):
    def __init__(self, bot_name, is_not_path: bool, file_name_or_path: str):
        super().__init__(is_not_path, file_name_or_path)
        self.bot_name = bot_name
        self.bot_phrases = {}
        self.bot_button_labels = {}
        self.bot_embeds = {}
        self.bot_modals = {}

    def get_bot_properties(self) -> dict[str, Any]:
        return super()._buffer[self.bot_name]

    def set_bot_properties(self, bot_properties: dict[str, Any]) -> None:
        super()._buffer[self.bot_name] = bot_properties


    """
    edit load func for filling field for fast interaction
    """
    def load_cfg(self) -> None:
        super().load_cfg()
        bot_props = self.get_bot_properties()
        self.bot_phrases = bot_props["phrases"]
        self.bot_button_labels = bot_props["button_labels"]
        self.bot_embeds = bot_props["embeds"]
        self.bot_modals = bot_props["modals"]
