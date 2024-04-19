from disnake.ext import commands


class Greeting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def reload(self):
        print("greeting перезагружен")

    # def is_setup_id(*ids):
    #     # ids = list(*ids)

    async def is_have_ids(self, *args):

        for key_discord_el in args:
            if self.bot.cfg["discord_ids"].get(key_discord_el) is None:
                self.bot.log.printf(f"[*/Greetings] отмена выполнения ~ {key_discord_el}")
                return False

        return True

    @commands.Cog.listener()
    async def on_member_join(self, member):
        res = await self.is_have_ids("greeting_ch")
        if not res:
            return
        await self.bot.get_channel(self.bot.cfg["discord_ids"]["greeting_ch"]).send(f"welcome to the server, {member.mention}")
        await member.edit(nick=member.name)


def setup(bot: commands.Bot):
    bot.add_cog(Greeting(bot))