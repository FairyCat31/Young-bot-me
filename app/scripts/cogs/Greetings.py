from app.scripts.cogs.DynamicConfig import DynamicConfigHelper
from app.scripts.components.smartdisnake import MEBot, SmartEmbed, ButtonView
from app.scripts.components.logger import LogType
from disnake import Member
from disnake.ext import commands
from random import randint


class Greeting(commands.Cog):
    def __init__(self, bot: MEBot):
        self.bot = bot
        self.msg_id = None
        self.view = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.view = ButtonView(self.bot.props["buttons/greeting_button_group"])

    @commands.Cog.listener(name="on_member_join")
    async def on_member_join(self, member: Member) -> None:
        await member.edit(nick=member.name)  # edit user nick to his id
        res = DynamicConfigHelper.is_cfg_setup(self.bot.props["dynamic_config"],
                                               "dm_greetings", "greeting_channel")
        if res:
            self.bot.log.printf(f"Parameter {res} is None", LogType.WARN)
            return

        # generate random first part of phrase
        greeting_phrases = self.bot.props["phrases/greetings"]
        greeting_random_phrase = greeting_phrases[randint(0, len(greeting_phrases)-1)]
        greeting_ch_phrase = greeting_random_phrase.format(user=member.mention)
        dm_embed = SmartEmbed(self.bot.props["embeds/greetings_dm"])
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


def setup(bot: MEBot):
    bot.add_cog(Greeting(bot))
