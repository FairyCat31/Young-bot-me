from disnake.ext import commands
from quart import jsonify

from app.scripts.cogs.UserVerify import UserVerify
from app.scripts.cogs.WebAPI.WebBase import WebBase, WebSession, Message
from app.scripts.utils.smartdisnake import SmartBot

class WebYoung(WebBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_verify: UserVerify | None = None
        self.init_quart_preset()

    def init_quart_preset(self):
        @self.web_app.route("/v1/<string:session_id>/ver_users", methods=["POST"], endpoint="ver_users")
        @self.session_route("access_token")
        @self.check_msg_validation(["names"])
        async def ver_users(session: WebSession, message: Message):
            names = message.content["names"]
            if type(names) is not str:
                return jsonify({"error": "names must have a str type"}), 400

            if self.user_verify is None:
                return jsonify({"error": "Module UserVerify is not available"}), 500

            result = await self.user_verify.verify(names)
            msg = Message(session, {"error": "", "output": result})
            print(type(msg.content))
            return jsonify(await msg.pack()), 201

    @commands.Cog.listener()
    async def on_ready(self):
        self.user_verify = self.bot.cogs.get("BuildUserVerify")
        await super().on_ready()


def setup(bot: SmartBot):
    bot.add_cog(WebYoung(bot))
