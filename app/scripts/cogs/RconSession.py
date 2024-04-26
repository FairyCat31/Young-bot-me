import disnake
from aiomcrcon import Client
from aiomcrcon import IncorrectPasswordError, RCONConnectionError, ClientNotConnectedError
from disnake.ext import commands
from disnake import Message, ApplicationCommandInteraction
from components.jsonmanager import JsonManager
import asyncio


class SmartRconSession:
    def __init__(self, rcon_host: str = "0.0.0.0", rcon_port: str = "25575", rcon_password: str = ""):
        self.rcon_host = rcon_host
        self.rcon_port = int(rcon_port)
        self.rcon_password = rcon_password
        print(self.rcon_host, self.rcon_port, self.rcon_password)
        self.client = Client(self.rcon_host, self.rcon_port, self.rcon_password)

    async def connect(self) -> (int, str):
        try:
            await self.client.connect()
        except RCONConnectionError as e:
            print(e)
            return 1, "An error occurred whilst connecting to the server..."

        except IncorrectPasswordError as e:
            print(e)
            return 2, "The provided password was incorrect..."

        return 0, ""

    async def send_cmd(self, command: str) -> (int, str):

        try:
            response, _ = await self.client.send_cmd(command)
        except ClientNotConnectedError:
            return 3, "The client was not connected to the server for some reason?"

        return 0, response

    async def close(self) -> None:
        await self.client.close()


class CommandRequest:
    def __init__(self, bot: disnake.ext.commands.Bot, message: disnake.Message):
        self.bot = message
        self.message = message
        self.permission_user_level = 0
        jsm = JsonManager()
        jsm.dload_cfg(short_name="em.json")
        self.cfg = jsm.buffer

    async def __send_cmd(self, command: str, session: SmartRconSession) -> str:
        _, response = await session.send_cmd(command)
        return response

    async def set_actual_permission_user_level(self) -> None:
        user = self.message.author  # user who use command
        temp = self.cfg.get(str(self.message.channel.id))
        actual_cfg = self.cfg.get("default") if temp is None else temp
        for role_id in actual_cfg["role_permission_level"].keys():
            if user.get_role(int(role_id)) is None:
                continue
            self.permission_user_level = int(actual_cfg["role_permission_level"].get(role_id))

    async def send_cmd(self, command: str, session: SmartRconSession) -> str:
        temp = self.cfg.get(str(self.message.channel.id))
        actual_cfg = self.cfg.get("default") if temp is None else temp
        separated_command = command.split(" ")
        separated_command[0] = separated_command[0].replace("/", "")
        allowed_cmd = []
        for i in range(self.permission_user_level, -1, -1):

            per = actual_cfg["allow_commands_to_level"].get(str(i))
            if per is None:
                continue

            allowed_cmd += per
        print(allowed_cmd)
        for cmd in allowed_cmd:
            if cmd == separated_command[0] or cmd == "*":

                return await self.__send_cmd(command, session)

        return "У тебя недостаточно прав, чтобы воспользоваться этой командой"


class RconSession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}
        self.my_cfg = JsonManager()
        self.my_cfg.dload_cfg("sessions.json")

    async def _restore_sessions(self):
        session_list = self.my_cfg.buffer.get("session_list")
        if session_list is None:
            return
        for session_card in session_list:
            self.sessions[session_card["channel_id"]] = SmartRconSession(
                rcon_host=session_card["rcon_host"],
                rcon_port=session_card["rcon_port"],
                rcon_password=session_card["rcon_password"]
            )
            response_code, response_message = await self.sessions[session_card["channel_id"]].connect()

            if response_code:
                self.bot.log.printf(f"[*\RconSession] cause error( {response_code} ) to connect >>> {session_card['rcon_host']}:{session_card['rcon_port']}")

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
                            description="Создать новую rcon сессию")
    @commands.default_member_permissions(administrator=True)
    async def session_start(self, inter: ApplicationCommandInteraction,
                            rcon_host: str = "127.0.0.1",
                            rcon_port: str = "25575",
                            rcon_password: str = ""
                            ) -> None:
        category = inter.guild.get_channel(1233522035444027477) # канал для сессий
        text_ch = await category.create_text_channel(name=f"{rcon_host}_{rcon_port}".replace(".", "_"))
        self.sessions[text_ch.id] = SmartRconSession(rcon_host=rcon_host, rcon_port=rcon_port, rcon_password=rcon_password)
        await self.sessions[text_ch.id].connect()
        await self._save_sessions()

        await inter.response.send_message(f"Запущена сессия {rcon_host}:{rcon_port}")

    @commands.slash_command(name="session_list",
                            description="Вывести все rcon сессии")
    @commands.default_member_permissions(administrator=True)
    async def session_list(self, inter: ApplicationCommandInteraction):
        msg = ""
        for key in self.sessions.keys():
            msg += f"<#{key}>\nhost >>> {self.sessions[key].rcon_host}\nport >>> {self.sessions[key].rcon_port}\npass >>> {self.sessions[key].rcon_password}\n"

        await inter.response.send_message(msg)

    @commands.slash_command(name="session_stop",
                            description="Закрыть rcon сессию")
    @commands.default_member_permissions(administrator=True)
    async def session_stop(self, inter: ApplicationCommandInteraction, channel_id: str) -> None:
        ch_id = int(channel_id)
        try:
            await self.sessions[ch_id].close()
            await inter.guild.get_channel(ch_id).delete()
            await inter.response.send_message(f"Сессия закрыта {self.sessions[ch_id].rcon_host}:{self.sessions[ch_id].rcon_port}")
            del self.sessions[ch_id]
            await self._save_sessions()
        except KeyError:
            print(self.sessions, ch_id)
            await inter.response.send_message(f"Не найдена сессия с айди канала {ch_id}")
        except Exception as e:
            print(e)

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        await self._restore_sessions()

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: Message):
        session_channel_ids = self.sessions.keys()
        if message.channel.id not in session_channel_ids:
            return

        # check if author is not bot
        if message.author.bot:
            return

        message_response = await message.channel.send(content="Команда отправлена :white_check_mark:\nЖдите ответа")

        cm = CommandRequest(bot=self.bot, message=message)
        await cm.set_actual_permission_user_level()
        response = await cm.send_cmd(command=message.content, session=self.sessions[message.channel.id])
        await message_response.edit(response)


def setup(bot: commands.Bot):
    bot.add_cog(RconSession(bot))