from app.scripts.components.smartdisnake import MEBot
from app.scripts.cogs.DynamicConfig.DynamicConfigHelper import is_cfg_setup
from app.scripts.components.logger import LogType
from disnake import ApplicationCommandInteraction
from disnake import Message, ChannelType, User, PermissionOverwrite
from disnake.ext import commands
from app.scripts.cogs.DMMessenger.DBHelper import DBManagerForDM
from datetime import datetime
DYN_REQ = ("dm_category", "moder_role", "unimice_guild")
MAX_PARSE_MESSAGES = 100
TWO_WEEK_UTC = 1209600


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
            name=self.bot.props["phrases/channel_dm_messenger"].format(user_name=user.name), overwrites=overwrites
        )
        return channel.id

    # Func for handling events

    async def _send_dm_msg_handler(self, msg: Message):
        res = self.dbm.get_dm_id(msg.author.id)
        if not res:
            ch_id = await self._create_dm_channel(msg.author)
            self.dbm.add_user_and_dm(msg.author.id, ch_id)
            res = self.dbm.get_dm_id(msg.author.id)

        if res < 0:
            await msg.author.create_dm()
            await msg.author.dm_channel.send(content=self.bot.props["phrases/bl_dm_msg"])
            return

        guild = self.bot.get_guild(self.bot.props["dynamic_config/unimice_guild"])
        channel = guild.get_channel(res)
        files = []
        for att in msg.attachments:
            files.append(await att.to_file())
        await channel.send(msg.content, files=files, stickers=msg.stickers)

    async def _send_category_msg_handler(self, msg: Message):
        uid = self.dbm.get_user_id(msg.channel.id)
        if not uid:
            nuid = self.dbm.get_user_id(-msg.channel.id)
            if not nuid:
                return
            await msg.channel.send(content=self.bot.props["phrases/bl_cat_msg"])
            return
        user = self.bot.get_user(uid)
        await user.create_dm()
        files = []
        for att in msg.attachments:
            files.append(await att.to_file())
        await user.dm_channel.send(msg.content, files=files, stickers=msg.stickers)

    async def _edit_dm_msg_handler(self, old_msg: Message, new_msg: Message):
        ch_id = self.dbm.get_dm_id(old_msg.author.id)
        channel = self.bot.get_channel(ch_id)
        async for message in channel.history(limit=MAX_PARSE_MESSAGES):
            # check: if author is bot, is content and files equal
            if message.author.id != self.bot.application_id:
                continue
            if message.content != old_msg.content:
                continue

            # var for content info about imposter attachments
            is_fake = False
            for i in range(len(old_msg.attachments)):
                if len(old_msg.attachments) != len(message.attachments):
                    is_fake = True
                    break
                old_msg_att = old_msg.attachments[i].to_dict()
                msg_att = message.attachments[i].to_dict()
                if old_msg_att["content_type"] != msg_att["content_type"]:
                    is_fake = True
                    break
                if old_msg_att["size"] != msg_att["size"]:
                    is_fake = True
                    break
                if old_msg_att["filename"] != msg_att["filename"]:
                    is_fake = True
                    break
            if is_fake:
                continue

            new_content = new_msg.content + f"\n-# ||{old_msg.content}||"
            new_files = []
            for att in new_msg.attachments:
                f = await att.to_file()
                new_files.append(f)
            await message.edit(content=new_content, files=new_files, attachments=[])
            break

    async def _edit_category_msg_handler(self, old_msg: Message, new_msg: Message):
        uid = self.dbm.get_user_id(old_msg.channel.id)
        user = self.bot.get_user(uid)
        await user.create_dm()
        async for message in user.dm_channel.history(limit=MAX_PARSE_MESSAGES):
            if message.author.id != self.bot.application_id:
                continue
            if message.content != old_msg.content:
                continue

            # var for content info about imposter attachments
            is_fake = False
            for i in range(len(old_msg.attachments)):
                if len(old_msg.attachments) != len(message.attachments):
                    is_fake = True
                    break
                old_msg_att = old_msg.attachments[i].to_dict()
                msg_att = message.attachments[i].to_dict()
                if old_msg_att["content_type"] != msg_att["content_type"]:
                    is_fake = True
                    break
                if old_msg_att["size"] != msg_att["size"]:
                    is_fake = True
                    break
                if old_msg_att["filename"] != msg_att["filename"]:
                    is_fake = True
                    break
            if is_fake:
                continue

            new_files = []
            for att in new_msg.attachments:
                f = await att.to_file()
                new_files.append(f)
            await message.edit(content=new_msg.content, files=new_files, attachments=[])
            break

    async def _del_dm_msg_handler(self, del_msg):
        ch_id = self.dbm.get_dm_id(del_msg.author.id)
        channel = self.bot.get_channel(ch_id)
        async for message in channel.history(limit=MAX_PARSE_MESSAGES):
            # check: if author is bot, is content and files equal
            if message.author.id != self.bot.application_id:
                continue
            if message.content != del_msg.content:
                continue

            # var for content info about imposter attachments
            is_fake = False
            for i in range(len(del_msg.attachments)):
                if len(del_msg.attachments) != len(message.attachments):
                    is_fake = True
                    break
                old_msg_att = del_msg.attachments[i].to_dict()
                msg_att = message.attachments[i].to_dict()
                if old_msg_att["content_type"] != msg_att["content_type"]:
                    is_fake = True
                    break
                if old_msg_att["size"] != msg_att["size"]:
                    is_fake = True
                    break
                if old_msg_att["filename"] != msg_att["filename"]:
                    is_fake = True
                    break
            if is_fake:
                continue

            new_content = del_msg.content + "\n-# пользователь удалил сообщение"
            await message.edit(content=new_content)
            break

    async def _del_category_msg_handler(self, del_msg):
        uid = self.dbm.get_user_id(del_msg.channel.id)
        user = self.bot.get_user(uid)
        await user.create_dm()
        async for message in user.dm_channel.history(limit=MAX_PARSE_MESSAGES):
            if message.author.id != self.bot.application_id:
                continue
            if message.content != del_msg.content:
                continue

            # var for content info about imposter attachments
            is_fake = False
            for i in range(len(del_msg.attachments)):
                if len(del_msg.attachments) != len(message.attachments):
                    is_fake = True
                    break
                old_msg_att = del_msg.attachments[i].to_dict()
                msg_att = message.attachments[i].to_dict()
                if old_msg_att["content_type"] != msg_att["content_type"]:
                    is_fake = True
                    break
                if old_msg_att["size"] != msg_att["size"]:
                    is_fake = True
                    break
                if old_msg_att["filename"] != msg_att["filename"]:
                    is_fake = True
                    break
            if is_fake:
                continue

            await message.delete()
            break

    # adds slash commands

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

    @commands.slash_command(name="block_dm")
    async def block_dm(self, inter: ApplicationCommandInteraction, discord_id: str):
        if not discord_id.isdigit():
            await inter.response.send_message(self.bot.props["phrases/inc_id"])
            return
        discord_id = int(discord_id)
        ch_id = self.dbm.get_dm_id(discord_id)
        if ch_id < 0:
            await inter.response.send_message(self.bot.props["phrases/already_bl"])
            return
        user = self.bot.get_user(discord_id)
        await inter.response.send_message(self.bot.props["phrases/bl_cat_msg"])
        if user is not None:
            await user.create_dm()
            await user.dm_channel.send(content=self.bot.props["phrases/bl_dm_msg"])
        ch = inter.guild.get_channel(ch_id)
        if ch is not None:
            await ch.send(content=self.bot.props["phrases/bl_cat_msg"])
        self.dbm.block_or_unblock_user(uid=discord_id, block=True)

    @commands.slash_command(name="unblock_dm")
    async def unblock_dm(self, inter: ApplicationCommandInteraction, discord_id: str):
        if not discord_id.isdigit():
            await inter.response.send_message(self.bot.props["phrases/inc_id"])
            return
        discord_id = int(discord_id)
        ch_id = self.dbm.get_dm_id(discord_id)
        if ch_id > 0:
            await inter.response.send_message(self.bot.props["phrases/already_unbl"])
            return
        await inter.response.send_message(self.bot.props["phrases/unbl_msg"])
        self.dbm.block_or_unblock_user(uid=discord_id, unblock=True)

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

    @commands.slash_command(name="close_old_dms")
    async def close_old_dms(self, inter: ApplicationCommandInteraction):
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

        guild = self.bot.get_guild(self.bot.props["dynamic_config/unimice_guild"])
        dm_category = guild.get_channel(self.bot.props["dynamic_config/dm_category"])

        need_to_del = []
        for ch in dm_category.channels:
            if ch.type != ChannelType.text:
                continue
            last_msg = ch.last_message
            if last_msg is None or datetime.now().timestamp() - last_msg.created_at.timestamp() > TWO_WEEK_UTC:
                need_to_del.append(ch.id)

        for ch_id in need_to_del:
            self.dbm.del_user_and_dm_by_chid(ch_id)
            ch = inter.guild.get_channel(ch_id)
            await ch.delete()

        await inter.response.send_message("Удалено %s каналов" % len(need_to_del))

    # Events handler

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
            await self._send_dm_msg_handler(msg)
        elif msg.channel.category_id == self.bot.props["dynamic_config/dm_category"]:
            await self._send_category_msg_handler(msg)
        return

    @commands.Cog.listener()
    async def on_message_edit(self, old_msg, new_msg):
        # check : is msg was sent by Bot
        if old_msg.author.id == self.bot.application_id:
            return
        # check: is dm category and unimice guild setup
        out = is_cfg_setup(self.bot.props["dynamic_config"], *DYN_REQ)
        if out:

            self.bot.log.printf(self.bot.props["phrases/parameter_not_set"].format(par=out), LogType.WARN)
            return
        # check : is msg was sent to DM or in dm category
        if old_msg.channel.type == ChannelType.private:
            await self._edit_dm_msg_handler(old_msg, new_msg)
        elif old_msg.channel.category_id == self.bot.props["dynamic_config/dm_category"]:
            await self._edit_category_msg_handler(old_msg, new_msg)
            pass
        return

    @commands.Cog.listener()
    async def on_message_delete(self, msg):
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
            await self._del_dm_msg_handler(msg)
            pass
        elif msg.channel.category_id == self.bot.props["dynamic_config/dm_category"]:
            await self._del_category_msg_handler(msg)
            pass
        return


def setup(bot: MEBot):
    bot.add_cog(DMMessenger(bot))
