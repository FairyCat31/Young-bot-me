from json import dump, load, loads, dumps
from typing import Any, Union, List
from os.path import exists
from app.scripts.components.crypter import CrypterDict
from dotenv import dotenv_values


PATH_CONFIG_JSON = "app/data/json/json_conf.json"


class AddressType:
    # default path > Young-bot-me/app/data/json
    FILE = "path_to_json_files"
    # default path > Young-bot-me/app/data/json/.crptjson
    CFILE = "path_to_crptjson_files"
    # default path > Where u start bot
    PATH = ""


class JsonManager:
    def __init__(self, address_type: str, file_name_or_path: str, smart_create: bool = True):
        """
        Manager for working json files
        """
        # load config for JsonManager in file json_conf.json
        with open(PATH_CONFIG_JSON, "r") as f:
            self.json_config = load(f)

        # set path and name file
        if address_type:
            self._name = file_name_or_path
            self._path = self.json_config[address_type] + self._name
        else:
            self._path = file_name_or_path
            self._name = self._path.split("/")[-1]
        # create dict which will content all data from file.json
        self._buffer = {}
        if not smart_create:
            return
        if exists(self._path):
            return
        self.write_in_file()

    def __str__(self):
        return dumps(self._buffer)

    def __getitem__(self, item) -> Union[str, int, dict, list, None]:
        # create vars
        item = str(item)
        object_output = self._buffer.copy()
        # get separator for pars items and path
        path_items = self.__path_items(item)
        # getting need element
        for path_item in path_items:
            object_output = object_output.get(path_item)

        return object_output

    def __setitem__(self, key, value):
        # create vars
        key = str(key)
        path_items = self.__path_items(key)
        len_items = len(path_items) - 1
        buffer = self._buffer
        # getting needed sector of dict
        for i, k in enumerate(path_items):
            if i == len_items:
                buffer[k] = value
                break
            # create empty dict if address is empty
            buffer.setdefault(k, {})

            buffer = buffer[k]

    def __path_items(self, line: str) -> List[str]:
        is_need_break = True
        separator = self.json_config["def_separator"]
        if line[0] == "%":
            i = 0
            separator = ""
            for s in line:
                i += 1
                if s == "%":
                    is_need_break = not is_need_break
                else:
                    separator += s

                if is_need_break:
                    break
            line = line[i:]
        path_items = line.split(separator)
        return path_items

    # write all data from file to buffer
    def load_from_file(self) -> None:
        with open(self._path, "r", encoding=self.json_config["encoding"]) as f:
            self._buffer = load(f)

    # write all data from buffer to file
    def write_in_file(self) -> None:
        with open(self._path, "w", encoding=self.json_config["encoding"]) as f:
            dump(self._buffer, f, indent=self.json_config["indent"])

    # get all content from buffer
    def get_buffer(self) -> dict[str, Any]:
        return self._buffer.copy()

    # set content to buffer
    def set_buffer(self, dictionary: dict) -> None:
        self._buffer = dictionary.copy()


class JsonManagerWithCrypt(JsonManager):
    def __init__(self, address_type: str,
                 file_name_or_path: str,
                 crypt_key: bytes = None):
        """
        Manager for working json files with crypt technologies


        """

        super().__init__(address_type=address_type, file_name_or_path=file_name_or_path, smart_create=False)
        self._crypter = self.__crypter_init(crypt_key)

    def __crypter_init(self, crypt_key: bytes) -> CrypterDict:
        if not crypt_key:
            env_vars = dotenv_values(self.json_config["env_with_crypt_key"])
            str_crypt_key = env_vars["DEFAULT_CRYPT_KEY"]
            crypt_key = str.encode(str_crypt_key, encoding="utf-8")

        crypter = CrypterDict(crypt_key=crypt_key)
        del env_vars, str_crypt_key, crypt_key
        return crypter

    def write_in_file(self) -> None:
        with open(self._path, "wb") as f:
            dict_as_encrypt_bytes = self._crypter.dict_encrypt(self._buffer)
            f.write(dict_as_encrypt_bytes)

    def load_from_file(self) -> None:
        with open(self._path, "rb") as f:
            encrypt_dict_as_bytes = f.read()
            self._buffer = self._crypter.dict_decrypt(encrypt_dict_as_bytes)


class JsonManagerForBots(JsonManager):
    def __init__(self, bot_name, address_type: str, file_name_or_path: str):
        super().__init__(address_type, file_name_or_path)
        self.bot_name = bot_name
        self.bot_phrases = {}
        self.bot_buttons = {}
        self.bot_embeds = {}
        self.bot_modals = {}

    # get only data for
    def get_bot_properties(self) -> dict[str, Any]:
        return self._buffer[self.bot_name].copy()

    def set_bot_properties(self, bot_properties: dict[str, Any]) -> None:
        self._buffer[self.bot_name] = bot_properties.copy()

    """
    edit load func for filling field for fast interaction
    """
    def load_from_file(self) -> None:
        super().load_from_file()
        bot_props = self.get_bot_properties()
        self.bot_phrases = bot_props["phrases"]
        self.bot_buttons = bot_props["buttons"]
        self.bot_embeds = bot_props["embeds"]
        self.bot_modals = bot_props["modals"]
