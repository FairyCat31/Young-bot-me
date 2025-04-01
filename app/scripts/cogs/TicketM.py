from disnake.ext import commands
from app.scripts.utils.smartdisnake import SmartBot, SmartEmbed
from disnake import ApplicationCommandInteraction, CategoryChannel, PermissionOverwrite, Guild, MessageInteraction
from disnake import Member, ButtonStyle
from disnake.ui import Button
from app.scripts.cogs.DynamicConfig import DynamicConfigShape as DynConf


CLOSE_TICKET_BTN = Button(custom_id="t_close", label="Закрыть тикет", style=ButtonStyle.red, emoji="✖")
OPEN_TICKET_BTN = Button(custom_id="t_open", label="Открыть тикет", style=ButtonStyle.green, emoji="💨")
class TicketM(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot
        self.START_EMBED = SmartEmbed(self.bot.props["embeds/ticket_embed"], {})
        self.TICKET_OPENER_EMBED = SmartEmbed(self.bot.props["embeds/open_ticket"], {})

    def _get_guild(self) -> Guild | None:
        return self.bot.get_guild(self.bot.props["dynamic_config/unimice_guild"])

    def _get_ticket_category(self) -> CategoryChannel | None:
        return self.bot.get_channel(self.bot.props["dynamic_config/ticket_category"])

    async def open_ticket(self, user_id: int):
        guild = self._get_guild()
        member = guild.get_member(user_id)
        overwrites = {
            member: PermissionOverwrite(view_channel=True, embed_links=True, attach_files=True),
            guild.default_role: PermissionOverwrite(view_channel=False),
            guild.me: PermissionOverwrite(view_channel=True, embed_links=True, attach_files=True)
        }
        moder_role = guild.get_role(self.bot.props["dynamic_config/worker_role"])
        overwrites[moder_role] = PermissionOverwrite(view_channel=True)
        ticket_category = self._get_ticket_category()
        ticket_channel = await ticket_category.create_text_channel(self.bot.props["phrases/ch_ticket_name"]
                                                                   .format(name=member.name),
                                                                   overwrites=overwrites)
        await ticket_channel.send(embed=self.START_EMBED, components=[CLOSE_TICKET_BTN])

    async def send_ticket_opener(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(embed=self.TICKET_OPENER_EMBED, components=[OPEN_TICKET_BTN])

    async def add_user(self, inter: ApplicationCommandInteraction, member: Member):
        if inter.channel.category_id != self.bot.props["dynamic_config/ticket_category"]:
            await inter.response.send_message(self.bot.props["phrases/only_ticket_cmd"])
            return

        channel = inter.channel
        overwrites = channel.overwrites
        overwrites[member] = PermissionOverwrite(view_channel=True, embed_links=True, attach_files=True)
        await channel.edit(overwrites=overwrites)
        await inter.response.send_message(self.bot.props["phrases/user_added"].format(nick=member.nick))

    async def close_ticket(self, inter: ApplicationCommandInteraction):
        if inter.channel.category_id != self.bot.props["dynamic_config/ticket_category"]:
            await inter.response.send_message(self.bot.props["phrases/only_ticket_cmd"])
            return

        await inter.channel.delete()

    @commands.Cog.listener()
    @DynConf.is_cfg_setup("unimice_guild", "ticket_category", "worker_role")
    async def on_button_click(self, inter: MessageInteraction):
        if inter.component.custom_id not in ["t_close", "t_open"]:
            return

        if inter.component.custom_id == "t_close":
            await inter.channel.delete()
        if inter.component.custom_id == "t_open":
            await self.open_ticket(inter.author.id)
            await inter.response.defer()

def build(bot: SmartBot):
    class BuildTicketM(TicketM):
        @commands.slash_command(**bot.props["cmds/snd_ticket"])
        @commands.default_member_permissions(administrator=True)
        async def send_ticket_opener(self, inter: ApplicationCommandInteraction):
            await super().send_ticket_opener(inter)

        @commands.slash_command(**bot.props["cmds/add_user"])
        @DynConf.has_any_roles("worker_role")
        async def add_user(self, inter: ApplicationCommandInteraction, member: Member):
            await super().add_user(inter, member)

        @commands.slash_command(**bot.props["cmds/close_ticket"])
        @DynConf.has_any_roles("worker_role")
        async def close_ticket(self, inter: ApplicationCommandInteraction):
            await super().close_ticket(inter)
    return BuildTicketM

def setup(bot: SmartBot):
    build_class = build(bot)
    bot.add_cog(build_class(bot))
