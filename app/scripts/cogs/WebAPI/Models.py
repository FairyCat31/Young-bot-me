import asyncio
from typing import Callable
from json import dumps
from datetime import datetime
from quart import Request
from app.scripts.utils.crypter import Hasher, gen_salt, gen_random_line
from jwt import decode as jwt_decode, encode as jwt_encode, InvalidSignatureError, InvalidIssuerError


TOKEN_LIFE = {
    "access_token": 3600,
    "refresh_token": 604800
}


class AuthToken:
    def __init__(self, tid: str, max_sessions: int,
                 token_salt: str, hashed_token: str,
                 reset_cookie: str, encoding: str = "latin1"):
        self.tid: str = tid
        self.max_sessions = max_sessions
        self._hashed_token: bytes = hashed_token.encode(encoding=encoding)
        self._reset_cookie: bytes = reset_cookie.encode(encoding=encoding)
        self._hasher: Hasher = Hasher("sha256", salt=token_salt.encode(encoding=encoding))

    def is_auth_token_valid(self, user_auth_token: str, encoding: str= "latin1") -> bool:
        hashed_user_auth_token = self._hasher.data_hash(user_auth_token.encode(encoding=encoding))
        return hashed_user_auth_token == self._hashed_token

    def is_reset_cookie_valid(self, user_reset_cookie: str, encoding: str= "latin1") -> bool:
        hashed_user_reset_cookie = self._hasher.data_hash(user_reset_cookie.encode(encoding=encoding))
        return hashed_user_reset_cookie == self._hashed_token


class JWToken:
    def __init__(self, sid: str, type_token: str, salt: bytes):
        payloads = {
            "iss": sid,
            "exp":TOKEN_LIFE[type_token] + datetime.now().timestamp(),
            "jti": gen_random_line(32)}
        headers = {
            "type": type_token
        }
        self._salt = salt
        self.iss = sid
        self.jti = payloads["jti"]
        self.raw: str = jwt_encode(payloads, salt, algorithm="HS256", headers=headers)

    def is_token_invalid(self, test_token) -> (dict, int):
        try:
            jwt_decode(test_token, self._salt, algorithms=["HS256"], issuer=self.iss)
            if self.raw == test_token:
                return {"error": ""}, 200
            return {"error": "Incorrect token. Use another token for auth."}, 403

        except InvalidSignatureError:
            return {"error": "Signature check failed. Token was edited by someone."}, 403
        except InvalidIssuerError:
            return {"error": "This token cant be used for auth with with user"}, 403


class WebSession:
    def __init__(self, tid: str, ip: str, on_delete: Callable):
        self.ip: str = ip
        self.tid: str = tid
        self.on_delete = on_delete
        self.sid: str = gen_random_line(24)
        self._session_salt = gen_salt(64)
        self.session_hasher = Hasher("sha256", salt=self._session_salt)
        self._access_token = JWToken(sid=self.sid, type_token="access_token", salt=self._session_salt)
        self._refresh_token = JWToken(sid=self.sid, type_token="refresh_token", salt=self._session_salt)

    async def on_session_expired(self):
        await asyncio.sleep(TOKEN_LIFE["refresh_token"]+1)
        self.on_delete(self.tid, self.sid)

    def is_invalid_auth(self, session_request: Request, token_type: str) -> (dict, int):
        if session_request.remote_addr != self.ip:
            return {"error": "This session was created for another device. Please choose another session"}, 403
        auth_header = session_request.authorization
        if auth_header is None:
            return {"error": "You re not auth for the using this route"}, 403
        auth_header = auth_header.token
        if auth_header is None:
            return {"error": "You re not auth for the using this route"}, 403
        if token_type == "refresh_token":
            check = self._refresh_token.is_token_invalid(auth_header)
        else:
            check = self._access_token.is_token_invalid(auth_header)
        return check


    def get_auth_data(self) -> dict:
        output = {
            "sid": self.sid,
            "salt": self._session_salt.decode("latin1"),
            "access_token": self._access_token.raw,
            "refresh_token": self._refresh_token.raw
        }
        return output

class Message:
    def __init__(self, session: WebSession, content: dict | None = None):
        self.umid: str | None = None
        self.session: WebSession = session
        self.required_params: list | None = None
        self.content: dict | None = content

    async def pack(self, exp_after: int = 60) -> dict:
        print(self.content)
        self.content["exp"] = int(datetime.now().timestamp() + exp_after)
        print(self.content)
        sign = self.session.session_hasher.data_hash(dumps(self.content).encode("latin1")).decode("latin1")
        self.content["signature"] = sign
        return self.content.copy()


    async def load_from_request(self, session_request: Request, required_params: list):
        self.content = await session_request.get_json(silent=True)
        self.required_params = required_params
        if self.content is not None:
            self.umid = self.content.get("umid")


    def is_invalid_message(self) -> (dict, int):
        if type(self.content) is not dict:
            return {"error": "Request must be in the json format"}, 400

        exp_check = self.is_expired_message()
        if exp_check[0]["error"]:
            return exp_check

        sign_check = self.is_signature_invalid()
        if sign_check[0]["error"]:
            return sign_check
        if None in [self.content.get(param) for param in self.required_params]:
            return {"error": f"Request is not complete. Missing important args for this method. Pls check docs for the fixing this problem"}, 400
        return {"error": ""}, 200


    def is_signature_invalid(self) -> (dict, int):
        sign = self.content.get("signature")
        if sign is None:
            return {"error": "Signature was not found"}, 400
        hasher = self.session.session_hasher
        temp_cont = self.content.copy()
        del temp_cont["signature"]
        temp_sign = hasher.data_hash(dumps(temp_cont).encode("latin1"))
        print(temp_sign.decode("latin1"), sign)
        if temp_sign.decode("latin1") == sign:

            return {"error": ""}, 200
        else:
            return {"error": "Request was edited by someone"}, 403

    def is_expired_message(self) -> (dict, int):
        exp_time = self.content.get("exp")
        if exp_time is None:
            return {"error": "Exp was not found"}, 400
        if datetime.now().timestamp() > exp_time:
            return {"error": "Request time was expired"}, 403
        else:
            return {"error": ""}, 200