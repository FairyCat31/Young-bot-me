from typing import Dict, List
from disnake.ext import commands
from hypercorn.asyncio import serve
from hypercorn.config import Config
from quart import Quart, request, jsonify
from app.scripts.utils.smartdisnake import SmartBot
from app.scripts.utils.ujson import JsonManager, AddressType
from app.scripts.cogs.WebAPI.Models import AuthToken, WebSession, Message

class WebBase(commands.Cog):
    def __init__(self, bot: SmartBot, name: str = "API"):
        self.bot = bot
        self.auth_tokens: Dict[str, AuthToken] = {}
        self.sessions_map: Dict[str, List[str]] = {}
        self.sessions: Dict[str, WebSession] = {}
        self.web_app = Quart(name)
        self.load_tokens()
        self.init_default_quart_preset()

    def session_route(self, token_type: str) -> (dict, int):
        def decorator(func):
            async def wrapper(session_id, *args, **kwargs):
                session = self.sessions.get(session_id)
                if session is None:
                    return {"error": "Session was not found. Please create a new session"}, 404
                check_auth = session.is_invalid_auth(request, token_type=token_type)
                if check_auth[0]["error"]:
                    return check_auth

                return await func(session, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def check_msg_validation(required_params: list | None = None):
        def decorator(func):
            async def wrapper(session, *args, **kwargs):
                message = Message(session)
                await message.load_from_request(request, required_params)
                msg_check = message.is_invalid_message()
                if msg_check[0]["error"]:
                    return msg_check
                return await func(session, message, *args, **kwargs)
            return wrapper
        return decorator

    def on_session_expired(self, tid: str, sid: str):
        if self.sessions.get(sid) is not None:
            del self.sessions[sid]
            self.sessions_map[tid].remove(sid)

    def load_tokens(self):
        jm = JsonManager(AddressType.FILE, "tokens.json")
        jm.load_from_file()
        for token in jm.buffer:
            self.sessions_map.setdefault(token["tid"], [])
            self.auth_tokens[token["tid"]] = AuthToken(tid=token["tid"],
                                                       max_sessions=token["limit"],
                                                       token_salt=token["salt"],
                                                       hashed_token=token["hashed_auth_token"],
                                                       reset_cookie=token["hashed_reset_cookie"])

    def init_default_quart_preset(self):
        @self.web_app.route("/v1/auth", methods=["POST"])
        async def auth():
            tid = request.args.get("tid")
            user_auth_token = request.args.get("auth_token")
            if tid is None or user_auth_token is None:
                return jsonify({"error": "Bad request. Please enter all arguments."}), 400
            auth_token = self.auth_tokens.get(tid)
            if auth_token is None:
                return jsonify({"error": "Bad request. Token wasn't found"}), 400
            if not auth_token.is_auth_token_valid(user_auth_token):
                return jsonify({"error": "Bad request. Use another one token."}), 400
            if len(self.sessions_map.get(tid)) >= auth_token.max_sessions:
                return jsonify({"error": "Bad request. The limit on the number of sessions has been reached"}), 400
            new_session = WebSession(tid, request.remote_addr, on_delete=self.on_session_expired)
            self.sessions_map[tid].append(new_session.sid)
            self.sessions[new_session.sid] = new_session
            return jsonify(new_session.get_auth_data()), 201

        @self.web_app.route("/v1/<string:session_id>/refresh_session",
                            methods=["POST"], endpoint="refresh_token")
        @self.session_route(token_type="refresh_token")
        async def refresh_session(session: WebSession):
            print(self.sessions_map)
            tid, sid = session.tid, session.sid
            new_session = WebSession(tid, session.ip, on_delete=self.on_session_expired)
            del self.sessions[sid]
            self.sessions_map[tid].remove(sid)
            self.sessions[new_session.sid] = new_session
            self.sessions_map[tid].append(new_session.sid)
            print(self.sessions_map)
            return jsonify(new_session.get_auth_data()), 201

        @self.web_app.route("/v1/<string:session_id>/close_session",
                            methods=["POST"], endpoint="close_session")
        @self.session_route(token_type="refresh_token")
        async def close_session(session: WebSession):
            print(self.sessions_map)
            tid, sid = session.tid, session.sid
            del self.sessions[sid]
            self.sessions_map[tid].remove(sid)
            print(self.sessions_map)
            return jsonify({"error": "", "output": "Session was deleted successful"}), 201


    @staticmethod
    def init_config_quart() -> Config:
        config = Config()
        #config.keyfile = "app/data/sys/cert.key"
        #config.certfile = "app/data/sys/cert.crt"
        config.bind = ['localhost:8080']
        return config

    def add_quart_to_async_task(self):
        self.bot.add_async_task(serve(self.web_app, WebBase.init_config_quart()))

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        self.bot.log.printf(f"Serving Quart app '{self.web_app.name}'")

        self.add_quart_to_async_task()


def setup(bot: SmartBot):
    bot.add_cog(WebBase(bot))
