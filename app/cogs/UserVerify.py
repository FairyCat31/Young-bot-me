from typing import Dict

from disnake import ApplicationCommandInteraction
from disnake import Member
from disnake.ext import commands

from app.cogs.DynamicConfig import DynamicConfigCog as DynConf
from app.utils.smartdisnake import SmartBot, SmartEmbed



__pyfactory_package__ = {
    "name": "user_verify",
    "version": "1",
    "dependencies": {
        "smartdisnake": "1",
        "dynamic_config": "1"
    }
}

class UserVerify(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot

    async def sl_verify(self, inter: ApplicationCommandInteraction, names: str):
        await inter.response.send_message("Обрабатываем запрос")
        res = await self.verify(names)
        output_msg = ""
        for name, is_accepted in res.items():
            if is_accepted:
                output_msg += f"{name} ✅ Игрок был одобрен\n"
            else:
                output_msg += f"{name} ❌ Игрок не найден\n"
        channel = inter.channel
        await channel.send(output_msg)

    async def verify(self, names: str) -> Dict[str, bool] | None:
        guild = self.bot.get_guild(self.bot.props["dynamic_config/unimice_guild"])
        if guild is None:
            return
        player_role = guild.get_role(self.bot.props["dynamic_config/player_role"])
        if player_role is None:
            return
        ch = guild.get_channel(self.bot.props["dynamic_config/channel_ver_info"])
        if ch is None:
            return
        embed = SmartEmbed(self.bot.props["embeds/accepted_forms"], {})
        result = {}
        pings = ""
        for name in names.split(" "):
            if not name:
                continue
            name = name.strip()
            user: Member = guild.get_member(int(name)) if name.isdigit() else guild.get_member_named(name)
            if user is None:
                result[name] = False
                continue
            pings += user.mention
            await user.add_roles(player_role)
            result[name] = True
        if pings:
            await ch.send(content=pings, embed=embed)
        return result

def build(bot: SmartBot):
    class BuildUserVerify(UserVerify):
        @commands.slash_command(**bot.props["cmds/verify"])
        @commands.guild_only()
        @commands.default_member_permissions(administrator=True)
        @DynConf.is_cfg_setup("player_role", "unimice_guild")
        async def sl_verify(self, inter: ApplicationCommandInteraction, names: str):
            return await super().sl_verify(inter, names)
    return BuildUserVerify

def setup(bot: SmartBot):
    build_class = build(bot)
    bot.add_cog(build_class(bot))
