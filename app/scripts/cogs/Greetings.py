from disnake.ext import commands
from random import randint


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

        greeting_replics = self.bot.cfg["replics"]["greetings"]  # get all replics
        greeting_random_replic = greeting_replics[randint(0, len(greeting_replics)-1)]  # random choose one
        greeting_random_replic = greeting_random_replic.format(user_mention=member.mention) # format replic (change {user_mention} on real mention)
        greeting_end_replic = self.bot.cfg["replics"]["greeting_info"]  # getting static info replic
        greeting_replic = f"{greeting_random_replic}\n\n{greeting_end_replic}"
        greeting_channel = self.bot.get_channel(self.bot.cfg["discord_ids"]["greeting_ch"])  # get greeting channel

        await greeting_channel.send(content=greeting_replic)  # send replic to chat
        await member.edit(nick=member.name)  # edit user nick to his id


def setup(bot: commands.Bot):
    bot.add_cog(Greeting(bot))