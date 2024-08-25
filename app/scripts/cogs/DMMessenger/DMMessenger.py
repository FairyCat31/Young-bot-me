from app.scripts.components.smartdisnake import MEBot
from app.scripts.cogs.DynamicConfig.DynamicConfigHelper import is_cfg_setup
from app.scripts.components.logger import LogType
from disnake import ApplicationCommandInteraction
from disnake import Message, ChannelType, User, PermissionOverwrite
from disnake.ext import commands
from app.scripts.cogs.DMMessenger.DBHelper import DBManagerForDM

DYN_REQ = ("dm_category", "moder_role", "unimice_guild")


class DMMessenger(commands.Cog):
    def __init__(self, bot: MEBot):
        self.bot = bot
        self.dbm = DBManagerForDM()
        self.dbm.save_start()

    async def _create_dm_channel(self, user: User) -> int:
        guild = self.bot.get_guild(self.bot.props["dynamic_config/unimice_guild"])

        # get dm_category
        dm_category = guild.get_channel(self.bot.props["dynamic_config/dm_category"])
        # get moder role
        moder_role = guild.get_role(self.bot.props["dynamic_config/moder_role"])
        overwrites = {
            moder_role: PermissionOverwrite(view_channel=True),  # добавляем роль модератора в доступ
            guild.default_role: PermissionOverwrite(view_channel=False),  # блокируем доступ everyone
            guild.me: PermissionOverwrite(view_channel=True, embed_links=True, attach_files=True)
        }
        channel = await dm_category.create_text_channel(
            name=self.bot.props["phrases/channel_dm_messenger"].format(user.name), overwrites=overwrites
        )
        return channel.id

    async def _dm_msg_handler(self, msg: Message):
        res = self.dbm.get_dm_id(msg.author.id)
        if not res:
            ch_id = await self._create_dm_channel(msg.author)
            self.dbm.add_user_and_dm(msg.author.id, ch_id)
            res = self.dbm.get_dm_id(msg.author.id)

        guild = self.bot.get_guild(self.bot.props["dynamic_config/unimice_guild"])
        channel = guild.get_channel(res)
        files = []
        for att in msg.attachments:
            files.append(await att.to_file())
        await channel.send(msg.content, files=files, stickers=msg.stickers)

    async def _category_msg_handler(self, msg: Message):
        res = self.dbm.get_user_id(msg.channel.id)
        user = msg.guild.get_member(res)
        await user.create_dm()
        files = []
        for att in msg.attachments:
            files.append(await att.to_file())
        await user.dm_channel.send(msg.content, files=files, stickers=msg.stickers)

    @commands.slash_command(name="open_dm")
    async def open_dm(self, inter: ApplicationCommandInteraction, user: User):
        # check: is cfg setup
        out = is_cfg_setup(self.bot.props["dynamic_config"], *DYN_REQ)
        if out:
            text_out = self.bot.props["phrases/parameter_not_set"].format(par=out)
            self.bot.log.printf(text_out, LogType.WARN)
            await inter.response.send_message(text_out)
            return
        # check: moder use this command
        if inter.user.get_role(self.bot.props["dynamic_config/moder_role"]) is None:
            await inter.response.send_message(
                content=self.bot.props["phrases/have_not_enough_rights"].format(user_mention=inter.author.mention),
                ephemeral=True)
            return
        ch_id = await self._create_dm_channel(user)
        self.dbm.add_user_and_dm(user.id, ch_id)
        await inter.response.send_message(self.bot.props["phrases/dm_open"].format(ch_id=ch_id))

    @commands.slash_command(name="close_dm")
    async def close_dm(self, inter: ApplicationCommandInteraction, user: User):
        # check: is cfg setup
        out = is_cfg_setup(self.bot.props["dynamic_config"], *DYN_REQ)
        if out:
            text_out = self.bot.props["phrases/parameter_not_set"].format(par=out)
            self.bot.log.printf(text_out, LogType.WARN)
            await inter.response.send_message(text_out)
            return

        # check: moder use this command
        if inter.user.get_role(self.bot.props["dynamic_config/moder_role"]) is None:
            await inter.response.send_message(
                content=self.bot.props["phrases/have_not_enough_rights"].format(user_mention=inter.author.mention),
                ephemeral=True)
            return

        ch_id = self.dbm.get_dm_id(user.id)
        self.dbm.del_user_and_dm(user.id)
        channel = inter.guild.get_channel(ch_id)
        if channel is not None:
            await channel.delete()
        await inter.response.send_message(self.bot.props["phrases/dm_close"])

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        # check : is msg was sent by Bot
        if msg.author.id == self.bot.application_id:
            return
        # check: is dm category and unimice guild setup
        out = is_cfg_setup(self.bot.props["dynamic_config"], *DYN_REQ)
        if out:

            self.bot.log.printf(self.bot.props["phrases/parameter_not_set"].format(par=out), LogType.WARN)
            return
        # check : is msg was sent to DM or in dm category
        if msg.channel.type == ChannelType.private:
            await self._dm_msg_handler(msg)
        elif msg.channel.category_id == self.bot.props["dynamic_config/dm_category"]:
            await self._category_msg_handler(msg)
        return


def setup(bot: MEBot):
    bot.add_cog(DMMessenger(bot))
