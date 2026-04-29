from json import dump, load
from pathlib import Path

from disnake.ext import commands
from disnake import Message, HTTPException, Forbidden

from app.utils.smartdisnake import SmartBot, SmartEmbed
from app.cogs.DynamicConfig import DynamicConfigCog as DynConf

freak_ban_cfg = Path("app/data/json/freak_ban.json")



class FreakBan(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot
        self.cfg = self.__init_cfg()

    @staticmethod
    def __init_cfg() -> dict:

            if not freak_ban_cfg.exists():
                with freak_ban_cfg.open("w") as f:
                    default = {"channel_id": -1}
                    dump(default, f)
                    return default

            with freak_ban_cfg.open("r") as f:
                return load(f)

    @commands.Cog.listener()
    @DynConf.is_cfg_setup("unimice_guild")
    async def on_ready(self):
        if self.cfg["channel_id"] < 0:
            guild =self.bot.get_guild(self.bot.props["dynamic_config/unimice_guild"])
            channel = await guild.create_text_channel("Ловушка джокера")
            embed = SmartEmbed(self.bot.props["embeds/spam_warning"], {})
            await channel.send("# ВНИМАНИЕ ⚠️\n## Если ты ОБЫЧНЫЙ ИГРОК, то немедлено ЗАКРОЙТЕ этот канал  🐭", embed=embed)

            self.cfg["channel_id"] = channel.id

            with freak_ban_cfg.open("w") as f:
                dump(self.cfg, f)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.channel.id != self.cfg["channel_id"]:
            return
        user = message.author

        try:
            await user.send("Вы были заблокированы автомодерацией за подозрительную активность(Спам рассылка)\nДля разбана напишите нам на нашу почту. Вы можете ее найти на нашем сайте https://unimice.ru")
        except HTTPException, Forbidden:
            self.bot.log.warn(f"Не удалось отправить предупреждение в лс пользователю {user.display_name}")

        try:
            await user.ban(clean_history_duration=86400, reason="Взлом аккаунта (Автомодер)")
        except Exception as e:
            self.bot.log.error(f"Не удалось забанить пользователя {user.display_name}\n{e}")



def build(bot: SmartBot):
    class BuildFreakBan(FreakBan):
        pass

    return BuildFreakBan


def setup(bot: SmartBot):
    build_class = build(bot)
    bot.add_cog(build_class(bot))
