from disnake.ext import commands
from disnake.ui import View, Button
import disnake
from components.dbmanager import DatabaseManager
from components.jsonmanager import JsonManager


class TestView(View):
    def __init__(self, block_previous_butt: bool = False, block_next_butt: bool = False):
        super().__init__()

        self.add_item(Button(label="◀", style=disnake.ButtonStyle.primary, custom_id="previous_user", row=0, disabled=block_previous_butt))
        self.add_item(Button(label="▶", style=disnake.ButtonStyle.primary, custom_id="next_user", row=0, disabled=block_next_butt))
        self.add_item(Button(label="Создать чат", style=disnake.ButtonStyle.gray, custom_id="open_dm", row=0, emoji="📃"))
        self.add_item(Button(label="Закрыть фул!", style=disnake.ButtonStyle.gray, custom_id="close_panel", row=0, emoji="⚠"))
        self.add_item(Button(label="Принять", style=disnake.ButtonStyle.green, custom_id="accept", row=1, emoji="✅"))
        self.add_item(Button(label="Отказать", style=disnake.ButtonStyle.red, custom_id="reject", row=1, emoji="⛔"))
        self.add_item(Button(label="Отказать с причиной", style=disnake.ButtonStyle.red, custom_id="reject_reason", row=1, emoji="📛"))


class Accepting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.panel = None
        self.user_dimension = {}
        self.cfg = JsonManager()
        self.cfg.dload_cfg(short_name="bots_properties.json")
        self.fields = {}
        self.dbm = DatabaseManager(file_name="registration.db")
        self.format_keys = ['did', 'login', 'name', 'gender', 'old', 'desc', 'way', 'inter', 'move', 'skill', 'soc']
        self.users = []
        self.user_panel_id = None
        self.func_dict = {
            "previous_user": self.func_previous_user,
            "next_user": self.func_next_user,
            "open_dm": self.func_open_dm,
            "close_panel": self.func_close_panel
            # "accept",
            # "reject",
            # "reject_reason"

        }

        for modal_key in self.cfg.buffer[self.bot.name]["modals"].keys():
            for field in self.cfg.buffer[self.bot.name]["modals"][modal_key]["text_inputs"]:
                self.fields[field["custom_id"][1:]] = field["label"]

    async def get_users(self) -> None:
        self.dbm.connect()

        for user_parse in self.dbm.users_get_id(table="PendingUsers"):
            user = {}
            for par in range(11):
                user[self.format_keys[par]] = user_parse[par]

            self.users.append(user)

        self.dbm.close()

    async def get_view(self, user_panel_id: int = 0) -> TestView:
        button_view = TestView(block_previous_butt= user_panel_id==0, block_next_butt= user_panel_id==len(self.users)-1)
        return button_view

    async def get_embed(self, moder_name: str, moder_avatar: str, uid: int = 0) -> disnake.Embed:
        user_data = self.users[uid]

        embed = disnake.Embed(
            title='{:-^42}'.format(f"АНКЕТА ИГРОКА {self.bot.get_user(user_data['did']).name.upper()}"),
            description='{:-^60}'.format('{:0>2}'.format(uid+1) + "/" + '{:0>2}'.format(len(self.users))),
            color=disnake.Colour.blurple(),
        )
        embed.set_footer(
            text=f"Moderator logged as {moder_name}",
            icon_url=moder_avatar,
        )
        embed.set_thumbnail(self.bot.get_user(user_data['did']).avatar.url)

        for i in range(1, len(self.format_keys)):
            embed.add_field(name=self.fields[self.format_keys[i]], value=user_data[self.format_keys[i]], inline=False)

        return embed

    @commands.slash_command(
        name="accept",
        description="Команда вызова панели для одобрения заявки",
    )
    async def accept(self, inter: disnake.ApplicationCommandInteraction):
        self.user_panel_id = 0
        await self.get_users()
        await inter.response.send_message(content="Открытие панели...", delete_after=3)
        embed = await self.get_embed(moder_name=inter.user.name, moder_avatar=inter.user.avatar.url)
        view = await self.get_view()
        self.panel = await inter.channel.send(embed=embed,
                                              view=view)

    async def func_open_dm(self, inter: disnake.MessageInteraction) -> None:
        category = inter.guild.get_channel(1225137236366856315) # id dms category
        user = inter.guild.get_member(self.users[self.user_panel_id]["did"])
        overwrites = {
            inter.guild.get_role(872884999047745556): disnake.PermissionOverwrite(view_channel=True),  # id moder role
            inter.guild.get_role(1225140475850129508): disnake.PermissionOverwrite(view_channel=False), # id member role
            inter.guild.me: disnake.PermissionOverwrite(view_channel=True),
            user: disnake.PermissionOverwrite(view_channel=True)
        }
        text_ch = await category.create_text_channel(name=f"dm {user.name}", overwrites=overwrites)
        embed = await self.get_embed(moder_name=inter.user.name, moder_avatar=inter.user.avatar.url, uid=self.user_panel_id)
        await text_ch.send(content=f"{user.mention} доброго времени суток\nПо вашей заявке есть вопросы у {inter.user.mention}\nТакже учтите, что другие проверяющие({inter.guild.get_role(872884999047745556)}) могут задать вам вопросы", embed=embed)
        await inter.response.defer()

    async def set_user(self, inter: disnake.MessageInteraction, user_panel_id: int = 0):
        self.user_panel_id = user_panel_id
        embed = await self.get_embed(moder_name=inter.user.name, moder_avatar=inter.user.avatar.url, uid=self.user_panel_id)
        view = await self.get_view(user_panel_id=self.user_panel_id)
        await self.panel.edit(embed=embed, view=view)

    async def func_previous_user(self, inter: disnake.MessageInteraction):
        await self.set_user(inter=inter, user_panel_id=self.user_panel_id-1)
        await inter.response.defer()

    async def func_next_user(self, inter: disnake.MessageInteraction):
        await self.set_user(inter=inter, user_panel_id=self.user_panel_id+1)
        await inter.response.defer()

    async def func_close_panel(self, inter: disnake.MessageInteraction) -> None:
        try:
            await inter.response.send_message(content="Панель закрыта", ephemeral=True)
            await self.panel.delete()
            self.users = []
            self.user_panel_id = None
        except Exception as e:
            print(e)

    @commands.Cog.listener(name="on_button_click")
    async def when_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in ["previous_user", "next_user", "open_dm", "close_panel", "accept", "reject", "reject_reason"]:
            return

        await self.func_dict[inter.component.custom_id](inter=inter)


def setup(bot: commands.Bot):
    bot.add_cog(Accepting(bot))