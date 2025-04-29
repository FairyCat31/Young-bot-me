from random import randint

from disnake import Member
from disnake.ext import commands

from app.utils.smartdisnake import SmartEmbed, SmartBot
from app.cogs.DynamicConfig import DynamicConfigCog as DynConf



__pyfactory_package__ = {
    "name": "greetings",
    "version": "1",
    "dependencies": {
        "smartdisnake": "1",
        "dynamic_config": "1"
    }
}

class Greeting(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot
        self.msg_id = None
        self.view = None

    @commands.Cog.listener(name="on_member_join")
    @DynConf.is_cfg_setup("dm_greetings", "greeting_channel")
    async def on_member_join(self, member: Member) -> None:
        await member.edit(nick=member.name)  # edit user nick to his id
        # generate random first part of phrase
        greeting_phrases = self.bot.props["phrases/greetings"]
        greeting_random_phrase = greeting_phrases[randint(0, len(greeting_phrases)-1)]
        greeting_ch_phrase = greeting_random_phrase.format(user=member.mention)
        dm_embed = SmartEmbed(self.bot.props["embeds/greetings_dm"], {"user": member.name})
        dm_embed.description = dm_embed.description.format(user=member.mention)
        # open dm with user and send phrase to him if this func enabled
        if self.bot.props["dynamic_config/dm_greetings"]:
            await member.create_dm()
            await member.dm_channel.send("", embed=dm_embed)

        # get chat id and check chat_id != 0
        chat_id = self.bot.props["dynamic_config/greeting_channel"]
        if chat_id:
            # get greeting channel
            greeting_channel = self.bot.get_channel(chat_id)
            await greeting_channel.send(greeting_ch_phrase)  # send phrase to chat


def setup(bot: SmartBot):
    bot.add_cog(Greeting(bot))
