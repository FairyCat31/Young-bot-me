from json import dump, load
from typing import Any
from os.path import exists


PATH_CONFIG_JSON = "app/data/json/json_conf.json"


class AddressType:
    # default path > Young-bot-me/app/data/json
    FILE = 1
    # default path > Where u start bot
    PATH = 0


class JsonManager:
    def __init__(self, type_address: int, file_name_or_path: str, smart_create: bool = True):
        """
        load config for working JsonManager

        default_path
        indent
        encoding
        """
        # load config for JsonManager in file json_conf.json
        with open(PATH_CONFIG_JSON, "r") as f:
            self.json_config = load(f)

        # set path and name file
        if type_address:
            self._name = file_name_or_path
            self._path = self.json_config["path_to_json_files"] + self._name
        else:
            self._path = file_name_or_path
            self._name = self._path.split("/")[-1]
        # create dict which will content all data from file.json
        self._buffer = {}
        if not smart_create:
            return
        if exists(self._path):
            return
        self.write_cfg()

    def __str__(self):
        return str(self._buffer)

    # write all data from file to buffer
    def load_cfg(self) -> None:
        with open(self._path, "r", encoding=self.json_config["encoding"]) as f:
            self._buffer = load(f)

    # write all data from buffer to file
    def write_cfg(self) -> None:
        with open(self._path, "w", encoding=self.json_config["encoding"]) as f:
            dump(self._buffer, f, indent=self.json_config["indent"])

    # get all content from buffer
    def get_buffer(self) -> dict[str, Any]:
        return self._buffer

    # set content to buffer
    def set_buffer(self, dictionary: dict) -> None:
        self._buffer = dictionary


class JsonManagerForBots(JsonManager):
    def __init__(self, bot_name, type_address: int, file_name_or_path: str):
        super().__init__(type_address, file_name_or_path)
        self.bot_name = bot_name
        self.bot_phrases = {}
        self.bot_buttons = {}
        self.bot_embeds = {}
        self.bot_modals = {}

    # get only data for
    def get_bot_properties(self) -> dict[str, Any]:
        return self._buffer[self.bot_name]

    def set_bot_properties(self, bot_properties: dict[str, Any]) -> None:
        self._buffer[self.bot_name] = bot_properties

    """
    edit load func for filling field for fast interaction
    """
    def load_cfg(self) -> None:
        super().load_cfg()
        bot_props = self.get_bot_properties()
        self.bot_phrases = bot_props["phrases"]
        self.bot_buttons = bot_props["buttons"]
        self.bot_embeds = bot_props["embeds"]
        self.bot_modals = bot_props["modals"]
