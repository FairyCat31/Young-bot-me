from disnake.ext import commands
from app.scripts.utils.smartdisnake import SmartBot


class Main(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot

    async def ping(self, inter):
        author = inter.author
        print(author.name, author.nick, author.global_name)
        await inter.response.send_message(self.bot.props["def_phrases/ping"])


def build(bot: SmartBot):
    class BuildMain(Main):
        @commands.slash_command(**bot.props["cmds/main_ping"])
        @commands.default_member_permissions(administrator=True)
        async def ping(self, inter):
            await super().ping(inter)

    return BuildMain


def setup(bot: SmartBot):
    build_class = build(bot)
    bot.add_cog(build_class(bot))
