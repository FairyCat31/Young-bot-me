from disnake.ext import commands
from app.scripts.utils.smartdisnake import SmartBot


class Main(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot

    async def ping(self, inter):
        author = inter.author
        name = author.name
        nick = getattr(author, "nick", None)
        global_name = getattr(author, "global_name", None)

        print(name, nick, global_name)
        await inter.response.send_message(self.bot.props["def_phrases/ping"])

    async def help(self, inter):
        print("Help")
        await inter.response.send_message(self.bot.props["def_phrases/help"])

def build(bot: SmartBot):
    class BuildMain(Main):

        @commands.slash_command(**bot.props["cmds/main_help"])
        @commands.default_member_permissions(administrator=True)
        async def help(self, inter):
            await super().help(inter)
        @commands.slash_command(**bot.props["cmds/main_ping"])
        @commands.default_member_permissions(administrator=True)
        async def ping(self, inter):
            await super().ping(inter)

    return BuildMain


def setup(bot: SmartBot):
    build_class = build(bot)
    bot.add_cog(build_class(bot))
