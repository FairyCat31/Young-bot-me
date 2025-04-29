from re import search as shape_search
from sys import path as sys_path
from json import load, dumps
from typing import Any, List
from os.path import exists
from pathlib import Path

from json5 import dump as dump5, load as load5
from dotenv import dotenv_values

from app.utils.crypter import Crypter


__pyfactory_package__ = {
    "name": "ujson",
    "version": "1",
    "dependencies": {
        "crypter": "1"
    }
}

PATH_CONFIG_JSON = "app/data/json/json_conf.json"
launch_path = sys_path[1] + "/"


class AddressType:
    # default path > Young-bot-me/app/data/json
    FILE = "path_to_json_files"
    # default path > Young-bot-me/app/data/json/.crptjson
    CFILE = "path_to_crptjson_files"
    # default path > Where u start bot
    PATH = ""


class Udict(dict):
    def __getattr__(self, item: str) -> Any:
        value = self.get(item)
        if value is None:
            return None
        elif type(value) is dict:
            return Udict(value)
        else:
            return value


class JsonManager:
    def __init__(self, address: str,
                 address_type: str = AddressType.FILE,
                 smart_create: bool = True):
        """
        Manager for working with .json files

        Args:
            address_type: use class AddressType for setting this parameter
            address: file path
            smart_create: create file if it not exists
        """
        # load config for JsonManager in file json_conf.json
        with open(launch_path + PATH_CONFIG_JSON, "r") as f:
            self.json_config = load(f)

        # set path and name file
        if address_type:
            self._name = address
            self._path = launch_path + self.json_config[address_type]

        else:
            self._path = "\\".join(address.split("/")[:-1])
            self._name = self._path.split("/")[-1]
        self._fullpath = self._path + self._name
        # create dict which will content all data from file.json
        self._buffer = {}
        if smart_create and not exists(self._path):
            self.write_in_file()

    # methods for buffer
    @property
    def buffer(self) -> dict:
        return self._buffer.copy()

    @buffer.setter
    def buffer(self, dictionary: dict) -> None:
        self._buffer = dictionary.copy()

    def __str__(self):
        return dumps(self._buffer)

    def __path_items(self, line: str) -> List[str]:  # split path to elements
        res_parse = shape_search("<&(.+?)>", line)
        if res_parse:
            separator = res_parse.group(1)
        else:
            separator = self.json_config["def_separator"]
        path_items = line.split(separator)
        return path_items

    def __getitem__(self, item) -> Any:  # method for get item from dict by class
        item = str(item)
        object_output = self._buffer.copy()
        # get separator for pars items and path
        path_items = self.__path_items(item)
        # getting need element
        for path_item in path_items:
            object_output = object_output.get(path_item)
            if object_output is None:
                return None

        return object_output

    def __setitem__(self, key, value) -> None:  # method for set item from dict by class
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

    def __getattr__(self, item: str) -> Any:
        value = self.get(item)
        if type(value) is dict:
            return Udict(value)
        else:
            return value

    # group of methods for working with dict buffer without getting them.
    def keys(self):
        return self._buffer.keys()

    def items(self):
        return self._buffer.items()

    def values(self):
        return self._buffer.values()

    # manager methods

    # write all data from file to buffer
    def load_from_file(self) -> None:
        with open(self._fullpath, "r", encoding=self.json_config["encoding"]) as f:
            self._buffer = load(f)

    # write all data from buffer to file
    def write_in_file(self) -> None:
        Path(self._path).mkdir(parents=True, exist_ok=True)
        with open(self._fullpath, "w", encoding=self.json_config["encoding"]) as f:
            f.write(dumps(self._buffer, indent=self.json_config["indent"]))


class JsonManagerWithCrypt(JsonManager):
    def __init__(self, address: str,
                 address_type: str = AddressType.CFILE,
                 crypt_key: bytes | None = None,
                 smart_create: bool = True):
        """
        Manager for working with encrypted .json files (.crptjson)

        Args:
            address_type: use class AddressType for setting this parameter
            address: file path
            crypt_key: symmetric key
        """

        super().__init__(address_type=address_type, address=address, smart_create=False)
        self._crypter = self.__crypter_init(crypt_key)
        if smart_create and not exists(self._path + self._name):
            self.write_in_file()

    def __crypter_init(self, crypt_key: bytes | None) -> Crypter:  # method for creating crypter
        if not crypt_key:
            env_vars = dotenv_values(self.json_config["env_with_crypt_key"])
            str_crypt_key = env_vars["DEFAULT_CRYPT_KEY"]
            crypt_key = str.encode(str_crypt_key, encoding="utf-8")
            del env_vars, str_crypt_key
        crypter = Crypter(crypt_key=crypt_key)
        del crypt_key
        return crypter

    def write(self) -> None:
        """Write buffer to file"""
        Path(self._path).mkdir(parents=True, exist_ok=True)
        with open(self._fullpath, "wb") as f:
            dict_as_encrypt_bytes = self._crypter.dict_encrypt(self._buffer)
            f.write(dict_as_encrypt_bytes)

    def load(self) -> None:
        """Load buffer from file"""
        with open(self._fullpath, "rb") as f:
            encrypt_dict_as_bytes = f.read()
            self._buffer = self._crypter.dict_decrypt(encrypt_dict_as_bytes)


class JsonManager5(JsonManager):
    """
    Manager for working with .json5 files
    """

    # read all data from file to buffer
    def load(self) -> None:
        with open(self._path, "r", encoding=self.json_config["encoding"]) as f:
            self._buffer = load5(f)

    # write all data from buffer to file
    def write(self) -> None:
        with open(self._path, "w", encoding=self.json_config["encoding"]) as f:
            dump5(self._buffer, f, indent=self.json_config["indent"])
