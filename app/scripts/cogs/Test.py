from disnake.ext import commands


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.slash_command(name="test_func")
    # async def test(self, inter):
    #     author = inter.author
    #     print(author.name, author.nick, author.global_name)
    #     await inter.response.send_message("test")


def setup(bot: commands.Bot):
    bot.add_cog(Test(bot))