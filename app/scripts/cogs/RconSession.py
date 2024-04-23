from aiomcrcon import Client as rconClient
from aiomcrcon import IncorrectPasswordError, RCONConnectionError, ClientNotConnectedError,
from disnake.ext import commands
from disnake import Message, ApplicationCommandInteraction
from components.jsonmanager import JsonManager


class SmartRconSession:
    def __init__(self, rcon_host: str = "0.0.0.0", rcon_port: str = "25575", rcon_password: str = ""):
        self.rcon_host = rcon_host
        self.rcon_port = int(rcon_port)
        self.rcon_password = rcon_password

        self.client = rconClient(host=rcon_host, port=rcon_port, password=rcon_password)

    async def connect(self) -> (int, str):
        try:
            await self.client.connect()
        except RCONConnectionError:
            return 1, "An error occurred whilst connecting to the server..."

        except IncorrectPasswordError:
            return 2, "The provided password was incorrect..."

        return 0, ""

    async def send_cmd(self, command: str) -> (int, str):

        try:
            response = await self.client.send_cmd(command)
        except ClientNotConnectedError:
            return 3, "The client was not connected to the server for some reason?"

        return 0, response

    async def close(self) -> None:
        await self.client.close()


class RconSession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}
        self.my_cfg = JsonManager()
        self.my_cfg.dload_cfg("sessions.json")



    async def _restore_sessions(self):
        session_list = self.my_cfg.buffer.get("session_list")
        """
        {
            session_list: [
            {
                "channel_id": int
                "rcon_host": str
                "rcon_port": int
                "rcon_password": str               
            }
            ]
        }
        """
        if session_list is None:
            return

        for session_card in session_list:
            self.sessions[session_card["channel_id"]] = SmartRconSession(
                rcon_host=session_card["rcon_host"],
                rcon_port=session_card["rcon_port"],
                rcon_password=session_card["channel_id"]
            )

            response_code, response_message = self.sessions[session_card["channel_id"]].connect()

            if response_code:
                self.bot.log.printf(f"[*\RconSession] cause error to connect >>> {session_card['rcon_host']}:{session_card['rcon_port']}")



    async def _save_sessions(self):
        #create session list
        session_list = []

        #save session's data to session_list
        for key_session in self.sessions.keys():
            session_card = {}
            session = self.sessions.get(key_session)

            session_card["channel_id"] = key_session
            session_card["rcon_host"] = session.rcon_host
            session_card["rcon_port"] = session.rcon_port
            session_card["rcon_password"] = session.rcon_password

            session_list.append(session_card)

        self.my_cfg.dwrite_cfg(
            {
                "session_list" : session_list
            }
        )


    @commands.slash_command(name="session_start",
                            description="Установить канал приветствия")
    @commands.default_member_permissions(administrator=True)
    async def session_start(self, inter: ApplicationCommandInteraction,
                            rcon_host: str = "0.0.0.0",
                            rcon_port: str = "25575",
                            rcon_password: str = ""
                            ) -> None:
        self.sessions[inter.channel] = rconClient(rcon_host=rcon_host, rcon_port=rcon_port, rcon_password=rcon_password)
        await self._save_sessions()


    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: Message):
        # check if message send in session chat
        session_channel_ids = self.sessions.keys()
        if message.channel not in session_channel_ids:
            return

        # check if author is not bot
        if message.author.bot:
            return







def setup(bot: commands.Bot):
    bot.add_cog(RconSession(bot))