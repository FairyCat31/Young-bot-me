from disnake.ext import commands


class Greeting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hello_channel_id = 872898518589767752

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.get_channel(self.hello_channel_id).send(f"welcome to the server, {member.mention}")
        await member.edit(nick=member.name)


def setup(bot: commands.Bot):
    bot.add_cog(Greeting(bot))