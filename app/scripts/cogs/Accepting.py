from disnake.ext import commands
from disnake.ui import View, Button
from asyncio import sleep
import disnake
from components.dbmanager import DatabaseManager
from components.jsonmanager import JsonManager
from components.smartdisnake import *


class TestView(View):
    def __init__(self, block_previous_butt: bool = False, block_next_butt: bool = False, block_full: bool = False):
        super().__init__()

        self.add_item(Button(label="◀", style=disnake.ButtonStyle.primary, custom_id="previous_user", row=0, disabled=block_full or block_previous_butt))
        self.add_item(Button(label="▶", style=disnake.ButtonStyle.primary, custom_id="next_user", row=0, disabled=block_full or block_next_butt))
        self.add_item(Button(label="Создать чат", style=disnake.ButtonStyle.gray, custom_id="open_dm", row=0, emoji="📃", disabled=block_full))
        self.add_item(Button(label="Закрыть фул!", style=disnake.ButtonStyle.gray, custom_id="close_panel", row=0, emoji="⚠"))
        self.add_item(Button(label="Принять", style=disnake.ButtonStyle.green, custom_id="accept", row=1, emoji="✅", disabled=block_full))
        self.add_item(Button(label="Отказать", style=disnake.ButtonStyle.red, custom_id="reject", row=1, emoji="⛔", disabled=block_full))
        self.add_item(Button(label="Отказать с причиной", style=disnake.ButtonStyle.red, custom_id="reject_reason", row=1, emoji="📛", disabled=block_full))


class ReasonModal(SmartModal):
    def __init__(self, cfg: dict):
        # The details of the modal, and its components
        self.ans = None
        super().__init__(modal_cfg=cfg)

    async def callback(self, inter: disnake.ModalInteraction):
        for _, value in inter.text_values.items():
            self.ans = value[:1024]
            break
        await inter.response.send_message(content="ok", ephemeral=True, delete_after=1)


class Accepting(commands.Cog):

    dio = {}

    def __init__(self, bot):
        self.bot = bot
        self.panel = None
        self.user_dimension = {}
        self.cfg = bot.cfg
        self.__class__.dio = self.cfg["discord_ids"]
        # self.cfg = JsonManager().buffer[self.bot.name]
        # self.cfg.dload_cfg(short_name="bots_properties.json")
        self.fields = {}
        self.dbm = DatabaseManager(file_name="registration.db")
        self.format_keys = ['did', 'login', 'name', 'gender', 'old', 'desc', 'way', 'inter', 'move', 'skill', 'soc']
        self.users = []
        self.user_panel_id = None
        self.func_dict = {
            "previous_user": self.func_previous_user,
            "next_user": self.func_next_user,
            "open_dm": self.func_open_dm,
            "close_dm": self.func_close_dm,
            "close_panel": self.func_close_panel,
            "accept": self.func_accept,
            "reject": self.func_reject,
            "reject_reason": self.func_reject_reason

        }

        for modal_key in self.cfg["modals"].keys():
            for field in self.cfg["modals"][modal_key]["text_inputs"]:
                self.fields[field["custom_id"][1:]] = field["label"]

    def reload(self):
        self.cfg = self.bot.cfg
        self.__class__.dio = self.cfg["discord_ids"]
        self.bot.log.printf(f"Modal {self.__class__.__name__} was reloaded")

    async def is_have_ids(self, *args):

        for key_discord_el in args:
            if self.bot.cfg["discord_ids"].get(key_discord_el) is None:
                self.bot.log.printf(f"[*/Accepting] отмена выполнения ~ {key_discord_el}")
                return False

        return True

    # lib methods for class -> Accepting

    def helper_accept_reject(accept: bool = False, reject: bool = False):
        def decorator(func):
            async def wrapper(self, inter: disnake.ModalInteraction, reason: str = "по личному решению администрации", **kwargs):
                try:
                    await inter.response.defer()
                except disnake.errors.InteractionResponded:
                    pass

                member = inter.guild.get_member(self.users[self.user_panel_id]["did"])
                channel = inter.guild.get_channel(self.bot.cfg["discord_ids"]["ver_result_ch"])  # результаты верифа
                if reject:
                    embed = await self.get_reject_embed(inter=inter, member=member, reason=reason)
                if accept:
                    embed = await self.get_accept_embed(inter=inter, member=member)

                await channel.send(content=member.mention, embed=embed)

                await func(self, inter=inter, reason=reason, member=member, **kwargs)

                await self.del_from_db()
                if accept:
                    await self.add_to_db()

                del self.users[self.user_panel_id]

                await self.save_set_user(inter=inter, user_panel_id=self.user_panel_id)

            return wrapper

        return decorator

    async def get_users(self) -> None:
        self.dbm.connect()

        for user_parse in self.dbm.users_get_id(table="PendingUsers"):
            user = {}
            for par in range(len(user_parse)):
                user[self.format_keys[par]] = user_parse[par]

            self.users.append(user)

        self.dbm.close()

    async def save_set_user(self, inter: disnake.MessageInteraction, user_panel_id: int = 0):
        try:
            var = self.users[user_panel_id]
            del var
        except IndexError:
            try:
                var = self.users[user_panel_id-1]
                del var
            except IndexError:
                pass
                embed = await self.get_empty_embed()
                view = TestView(block_full=True)
                await self.panel.edit(embed=embed, view=view)

            else:
                await self.set_user(inter=inter, user_panel_id=user_panel_id-1)
        else:
            await self.set_user(inter=inter, user_panel_id=user_panel_id)

    async def set_user(self, inter: disnake.MessageInteraction, user_panel_id: int = 0):
        self.user_panel_id = user_panel_id
        embed = await self.get_embed(moder_name=inter.user.name, moder_avatar=inter.user.display_avatar.url, uid=self.user_panel_id)
        view = await self.get_view(user_panel_id=self.user_panel_id)
        await self.panel.edit(content="", embed=embed, view=view)

    async def add_to_db(self, table: str = "AcceptedUsers"):
        self.dbm.connect()
        self.dbm.user_add_2(table=table, ud=self.users[self.user_panel_id], discord_id=self.users[self.user_panel_id]["did"])
        self.dbm.commit()
        self.dbm.close()

    async def del_from_db(self, table: str = "PendingUsers"):
        self.dbm.connect()
        self.dbm.user_delete(discord_id=self.users[self.user_panel_id]["did"], table=table)
        self.dbm.commit()
        self.dbm.close()

    # component methods ->(disnake) for class -> Accepting

    async def get_view(self, user_panel_id: int = 0) -> TestView:
        button_view = TestView(block_previous_butt=user_panel_id == 0, block_next_butt=user_panel_id == len(self.users)-1)
        return button_view

    async def get_embed(self, moder_name: str, moder_avatar: str, uid: int = 0) -> disnake.Embed:
        user_data = self.users[uid]

        embed = disnake.Embed(
            title='{:-^42}'.format(f"АНКЕТА ИГРОКА {self.bot.get_user(user_data['did']).name.upper()}"),
            description='{:-^60}'.format('{:0>2}'.format(uid+1) + "/" + '{:0>2}'.format(len(self.users))),
            color=disnake.Colour.blurple(),
        )
        embed.set_footer(
            text=self.cfg["embeds"]["request_accept"]["other"]["footer_text"].format(moder_name=moder_name),
            icon_url=moder_avatar,
        )
        embed.set_thumbnail(self.bot.get_user(user_data['did']).display_avatar.url)

        for i in range(1, len(self.format_keys)):
            embed.add_field(name=self.fields[self.format_keys[i]], value=user_data[self.format_keys[i]], inline=False)

        return embed

    async def get_accept_embed(self, inter: disnake.MessageInteraction, member: disnake.Member) -> SmartEmbed:
        embed = SmartEmbed(cfg=self.cfg["embeds"]["request_accept"])
        embed.title = embed.title.format(user_name=member.name).upper()
        embed.color = disnake.Colour.brand_green()

        embed.set_footer(
            text=self.cfg["embeds"]["request_accept"]["other"]["footer_text"].format(moder_name=inter.user.name),
            icon_url=inter.user.avatar.url,
        )

        return embed

    async def get_reject_embed(self, inter: disnake.MessageInteraction, member: disnake.Member, reason: str) -> disnake.Embed:
        embed = SmartEmbed(cfg=self.cfg["embeds"]["request_reject"])
        embed.title = embed.title.format(user_name=member.name).upper()
        embed.color = disnake.Colour.brand_red()

        embed.add_field(name=self.cfg["embeds"]["request_reject"]["other"]["field"]["name"],
                        value=self.cfg["embeds"]["request_reject"]["other"]["field"]["value"].format(reason=reason),
                        inline=self.cfg["embeds"]["request_reject"]["other"]["field"]["inline"])

        embed.set_footer(
            text=self.cfg["embeds"]["request_accept"]["other"]["footer_text"].format(moder_name=inter.user.name),
            icon_url=inter.user.avatar.url,
        )

        return embed

    async def get_empty_embed(self):
        embed = SmartEmbed(cfg=self.cfg["embeds"]["empty_embed"])
        embed.color = disnake.Color.greyple()
        return embed

    # button methods for class -> Accepting

    async def func_previous_user(self, inter: disnake.MessageInteraction) -> None:
        await self.set_user(inter=inter, user_panel_id=self.user_panel_id-1)
        await inter.response.defer()

    async def func_next_user(self, inter: disnake.MessageInteraction) -> None:
        await self.set_user(inter=inter, user_panel_id=self.user_panel_id+1)
        await inter.response.defer()

    async def func_open_dm(self, inter: disnake.MessageInteraction) -> None:
        category = inter.guild.get_channel(self.bot.cfg["discord_ids"]["dm_category"]) # категория для дм
        user = inter.guild.get_member(self.users[self.user_panel_id]["did"])
        overwrites = {
            inter.guild.get_role(self.bot.cfg["discord_ids"]["moder_role"]): disnake.PermissionOverwrite(view_channel=True),  # роль проверяющего
            inter.guild.get_role(self.bot.cfg["discord_ids"]["member_role"]): disnake.PermissionOverwrite(view_channel=False),  # роль участника
            inter.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
            inter.guild.me: disnake.PermissionOverwrite(view_channel=True, embed_links=True),
            user: disnake.PermissionOverwrite(view_channel=True)
        }
        text_ch = await category.create_text_channel(name=self.cfg["replics"]["dm_ch_name"].format(member_name=user.name), overwrites=overwrites)
        embed = await self.get_embed(moder_name=inter.user.name, moder_avatar=inter.user.avatar.url, uid=self.user_panel_id)
        await text_ch.send(content=self.cfg["replics"]["dm_start_message"].format(user_mention=user.mention, moder_mention=inter.user.mention, role_moder=inter.guild.get_role(self.bot.cfg["discord_ids"]["moder_role"]).mention),
                           embed=embed,
                           components=[
                               Button(label="Закрыть дм", style=disnake.ButtonStyle.primary, custom_id="close_dm",  emoji="⏹")
                           ]
                           )
        await inter.response.defer()

    async def func_close_dm(self, inter: disnake.MessageInteraction) -> None:
        await inter.channel.delete()
        await inter.response.defer()

    @helper_accept_reject(accept=True)
    async def func_accept(self, inter: disnake.MessageInteraction, member: disnake.Member, *args, **kwargs) -> None:
        await member.edit(nick=self.users[self.user_panel_id]["login"])
        await member.add_roles(inter.guild.get_role(self.bot.cfg["discord_ids"]["player_role"])) # роль игрока

    @helper_accept_reject(reject=True)
    async def func_reject(self, inter: disnake.MessageInteraction, reason: str = "по личному решению администрации", *args, **kwargs) -> None:
        pass

    async def func_reject_reason(self, inter: disnake.MessageInteraction) -> None:
        modal = ReasonModal(cfg=self.cfg["modals"]["reason_reject"])
        await inter.response.send_modal(modal=modal)
        while modal.ans is None:
            await sleep(0.5)
        reason = modal.ans
        await self.func_reject(inter=inter, reason=reason)

    async def func_close_panel(self, inter: disnake.MessageInteraction) -> None:
        try:
            await inter.response.send_message(content=self.cfg["replics"]["close_panel"], ephemeral=True)
            await self.panel.delete()
            self.users = []
            self.user_panel_id = None
        except Exception as e:
            print(e)

    # "commands" methods for class -> Accepting

    @commands.slash_command(
        name="accept_panel",
        description="Команда вызова панели для одобрения заявки",
    )
    async def panel(self, inter: disnake.ApplicationCommandInteraction):
        res = await self.is_have_ids("dm_category", "moder_role", "member_role", "player_role", "ver_result_ch")
        if not res:
            await inter.response.defer()
            return

        if inter.user.get_role(self.cfg["discord_ids"].get("moder_role")) is None:
            await inter.response.send_message(content=self.cfg["replics"]["have_not_enough_rights"], ephemeral=True)
            return

        self.user_panel_id = 0
        await self.get_users()
        await inter.response.send_message(content=self.cfg["replics"]["open_panel"], delete_after=3)
        self.panel = await inter.channel.send(content=self.cfg["replics"]["open_panel_wait"])
        await self.save_set_user(inter=inter, user_panel_id=0)

    @commands.Cog.listener(name="on_button_click")
    async def when_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in ["previous_user", "next_user", "open_dm", "close_dm", "close_panel", "accept", "reject", "reject_reason"]:
            return

        if inter.user.get_role(self.cfg["discord_ids"].get("moder_role")) is None:
            await inter.response.send_message(content=self.cfg["replics"]["have_not_enough_rights"], ephemeral=True)
            return

        await self.func_dict[inter.component.custom_id](inter=inter)


def setup(bot: commands.Bot):
    bot.add_cog(Accepting(bot))