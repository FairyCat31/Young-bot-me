from cryptography.fernet import Fernet
from json import loads, dumps


class Crypter:
    """
    Class for easy decrypt and encrypt STR
    """
    def __init__(self, crypt_key: bytes, encoding: str = "utf-8"):
        self.f = Fernet(crypt_key)
        self.encoding = encoding

    def encrypt(self, line: str) -> bytes:
        """ Func for encrypt python str

        Scheme

        Str -> encrypt bytes
        """
        str_as_bytes = str.encode(line, encoding=self.encoding)  # convert data type of str to bytes
        encrypt_data = self.f.encrypt(str_as_bytes)  # encrypt data
        return encrypt_data

    def decrypt(self, line: bytes) -> str:
        """ Func for decrypt python str

        Scheme

        Decrypt bytes -> Str
        """
        decrypt_data = self.f.decrypt(line)  # decrypt data
        bytes_as_str = decrypt_data.decode(encoding=self.encoding)  # convert data type of bytes to str
        return bytes_as_str


class CrypterDict(Crypter):
    def dict_encrypt(self, dict_for_encrypt: dict) -> bytes:
        """ Func for encrypt python dict

        ####

        Short scheme

        Dict -> encrypt bytes

        ####

        Long scheme

        Dict -> str -> bytes -> encrypt bytes
        """
        dict_as_str = dumps(dict_for_encrypt)  # convert data type of dict to str
        result = super().encrypt(dict_as_str)  # convert to bytes + encrypt
        return result

    def dict_decrypt(self, dict_for_decrypt: bytes) -> dict:
        """ Func for encrypt python dict

        ####

        Short scheme

        Encrypt bytes -> dict

        ####

        Long scheme

        Encrypt bytes -> bytes -> str -> dict
        """
        result_in_str = super().decrypt(dict_for_decrypt)  # decrypt + convert to str
        final_dict = loads(result_in_str)  # convert data type of str to dict
        return final_dict
