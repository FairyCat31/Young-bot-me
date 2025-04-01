from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from json import loads, dumps
from os import urandom
import hashlib
from random import randint
from string import ascii_letters, digits


SYM_IDS = ascii_letters + digits
SYM_LEN = len(SYM_IDS) - 1


def gen_random_line(len_id: int = 8) -> str:
    result = "".join([SYM_IDS[randint(0, SYM_LEN)] for i in range(len_id)])
    return result


def gen_salt(size: int = 32) -> bytes:  # generate random bytes
    return urandom(size)


class CrypterConvertor:
    def __init__(self, encoding: str):
        self.encoding = encoding

    @staticmethod
    def encrypt(data: bytes) -> bytes: return data  # pattern for encrypt method
    @staticmethod
    def decrypt(data: bytes) -> bytes: return data  # pattern for decrypt method

    def str_encrypt(self, line: str) -> bytes:
        """ Func for encrypt bytes
        Scheme
        Str -> Encrypted bytes"""
        str_as_bytes = line.encode(encoding=self.encoding)
        encrypt_data = self.encrypt(str_as_bytes)
        return encrypt_data

    def str_decrypt(self, data: bytes) -> str:
        """ Func for decrypt bytes
        Scheme
        Encrypted bytes -> Str"""
        decrypt_data = self.decrypt(data)
        bytes_as_str = decrypt_data.decode(encoding=self.encoding)
        return bytes_as_str

    def dict_encrypt(self, dict_for_encrypt: dict) -> bytes:
        """ Func for encrypt dict
        Scheme
        Dict -> encrypt bytes"""
        dict_as_str = dumps(dict_for_encrypt)
        result = self.str_encrypt(dict_as_str)
        return result

    def dict_decrypt(self, dict_for_decrypt: bytes) -> dict:
        """ Func for encrypt python dict
        Scheme
        Encrypt bytes -> dict """
        result_in_str = self.str_decrypt(dict_for_decrypt)
        result = loads(result_in_str)
        return result


class Crypter(CrypterConvertor):
    """
    Class for easy decrypt and encrypt STR using symmetric algorithm
    """
    def __init__(self, crypt_key: bytes, encoding: str = "latin1"):
        """
        crypt_key - symmetric key, which using for decrypt and encrypt data
        encoding - encoding for the convertation data from bytes to string DEFAULT: latin1
        """
        super().__init__(encoding)
        self.__fernet = Fernet(crypt_key)

    def encrypt(self, data: bytes) -> bytes:
        """ Func for encrypt bytes
        Scheme
        Bytes -> Encrypted bytes"""
        encrypt_data = self.__fernet.encrypt(data)  # encrypt data
        return encrypt_data

    def decrypt(self, line: bytes) -> bytes:
        """ Func for decrypt bytes
        Scheme
        Encrypted bytes -> Bytes"""
        decrypt_data = self.__fernet.decrypt(line)  # decrypt data
        return decrypt_data


class AsymmetricCrypter(CrypterConvertor):
    """
    Class for easy decrypt and encrypt STR using asymmetric algorithm
    """
    def __init__(self, private_key: rsa.RSAPrivateKey | None = None,
                 public_key: rsa.RSAPublicKey | None = None,
                 encoding: str = "latin1"):
        """
        private_key - asymmetric key, which using for decrypt data
        public_key - asymmetric key, which using for encrypt data
        encoding - encoding for the convertation data from bytes to string DEFAULT: latin1
        """
        super().__init__(encoding)
        self.__private_key = private_key
        self.__public_key = public_key
        self.__padding = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                      algorithm=hashes.SHA256(),
                                      label=None)

    @property
    def public_key(self) -> bytes | None:  # getter for var public key
        return self.__public_key.public_bytes(
                   encoding=serialization.Encoding.PEM,
                   format=serialization.PublicFormat.SubjectPublicKeyInfo
               )

    @public_key.setter
    def public_key(self, value: bytes):  # setter for var public key
        self.__public_key = serialization.load_pem_public_key(value)

    def generate_keys(self, key_size: int = 2048) -> None:  # generate a pair of asymmetric keys
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.__public_key = self.__private_key.public_key()

    def encrypt(self, data: bytes) -> bytes:
        """ Func for encrypt bytes
        Scheme
        Bytes -> Encrypted bytes"""
        encrypted_data = self.__public_key.encrypt(data, self.__padding)
        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        """ Func for encrypt bytes
        Scheme
        Encrypted bytes -> Bytes"""
        decrypted_data = self.__private_key.decrypt(data, self.__padding)
        return decrypted_data


class Hasher:
    def __init__(self, hash_name: str, salt: bytes | int = None):
        self.hash_name = hash_name

        # setting salt
        t_salt = type(salt)
        if t_salt is bytes:
            self.salt = salt
        else:
            self.salt = gen_salt(salt if t_salt is int else 32)

    def data_hash(self, data: bytes, iters: int = 100):
        return hashlib.pbkdf2_hmac(self.hash_name, data, self.salt, iters)
