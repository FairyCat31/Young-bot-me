from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from components.jsonmanager import JsonManager


class YoungMouseMain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jsm = JsonManager()
        self.jsm.dload_cfg("ym.json")
        bot.cfg["discord_ids"] = self.jsm.buffer
        self.req_fields = ["setup", "dm_category", "moder_role", "member_role", "player_role", "ver_result_ch", "greeting_ch"]

    def reload(self):
        print("ymm перезагружен")

    """
    "dm_category": "категория для дм"
    "moder_role": "роль проверяющего"
    "member_role": "роль участника"
    "player_role": "роль игрока"
    "ver_result_ch": "текст канал вериф резалт"
    "greeting_ch": "текст канал приветствия"
    """

    @commands.slash_command(name="msg",
                            description="-")
    @commands.default_member_permissions(administrator=True)
    async def msg(self, inter: ApplicationCommandInteraction, text: str, channel: str = "1219502611896467482"):
        await inter.guild.get_channel(int(channel)).send(content=text)
        await inter.response.send_message(content=f"send \"{text}\" to channel (id: {channel})", delete_after=10)

    @commands.slash_command(name="setup_show_config",
                            description="Показать текущие настройки")
    @commands.default_member_permissions(administrator=True)
    async def setup_show_config(self, inter: ApplicationCommandInteraction):
        sett = self.bot.cfg["discord_ids"]
        message = ""
        for key in self.req_fields:
            message += f"\n{key} ---> {sett.get(key)}"

        await inter.response.send_message(message)

    async def update_setup_data(self):
        # is_content_none = False
        # for key in self.req_fields:
        #     is_content_none = is_content_none and (self.bot.cfg["discord_ids"].get(key) is None

        if not (None in [self.bot.cfg["discord_ids"].get(key) for key in self.req_fields]) and not self.bot.cfg["discord_ids"]["setup"]:
            self.bot.cfg["discord_ids"]["setup"] = True

        self.jsm.dwrite_cfg(dictionary=self.bot.cfg["discord_ids"])

    @commands.slash_command(name="setup_dm_category",
                            description="Установить категорию для создания дм")
    @commands.default_member_permissions(administrator=True)
    async def setup_dm_category(self, inter: ApplicationCommandInteraction,
                                dm_category_id: str):
        self.bot.cfg["discord_ids"]["dm_category"] = int(dm_category_id)
        await inter.response.send_message(f"dm category id set --> {dm_category_id}")
        await self.update_setup_data()

    @commands.slash_command(name="setup_moder_role",
                            description="Установить роль проверяющего")
    @commands.default_member_permissions(administrator=True)
    async def setup_moder_role(self, inter: ApplicationCommandInteraction,
                                moder_role_id: str):
        self.bot.cfg["discord_ids"]["moder_role"] = int(moder_role_id)
        await inter.response.send_message(f"moder role id set --> {moder_role_id}")
        await self.update_setup_data()

    @commands.slash_command(name="setup_member_role",
                            description="Установить роль участника")
    @commands.default_member_permissions(administrator=True)
    async def setup_member_role(self, inter: ApplicationCommandInteraction,
                               member_role_id: str):
        self.bot.cfg["discord_ids"]["member_role"] = int(member_role_id)
        await inter.response.send_message(f"member role id set --> {member_role_id}")
        await self.update_setup_data()

    @commands.slash_command(name="setup_player_role",
                            description="Установить роль за верификацию")
    @commands.default_member_permissions(administrator=True)
    async def setup_player_role(self, inter: ApplicationCommandInteraction,
                                player_role_id: str):
        self.bot.cfg["discord_ids"]["player_role"] = int(player_role_id)
        await inter.response.send_message(f"player role id set --> {player_role_id}")
        await self.update_setup_data()

    @commands.slash_command(name="setup_ver_result_ch",
                            description="Установить канал для результатов")
    @commands.default_member_permissions(administrator=True)
    async def setup_ver_result_ch(self, inter: ApplicationCommandInteraction,
                                ver_result_ch_id: str):
        self.bot.cfg["discord_ids"]["ver_result_ch"] = int(ver_result_ch_id)
        await inter.response.send_message(f"ver result channel id set --> {ver_result_ch_id}")
        await self.update_setup_data()

    @commands.slash_command(name="setup_greeting_ch",
                            description="Установить канал приветствия")
    @commands.default_member_permissions(administrator=True)
    async def setup_greeting_ch(self, inter: ApplicationCommandInteraction,
                                greeting_ch_id: str):
        self.bot.cfg["discord_ids"]["greeting_ch"] = int(greeting_ch_id)
        await inter.response.send_message(f"ver result channel id set --> {greeting_ch_id}")
        await self.update_setup_data()

    @commands.slash_command(name="setup_all",
                            description="Настройка всех параметров бота")
    @commands.default_member_permissions(administrator=True)
    async def multi_setup(self, inter: ApplicationCommandInteraction ):
        pass


def setup(bot: commands.Bot):
    bot.add_cog(YoungMouseMain(bot))



