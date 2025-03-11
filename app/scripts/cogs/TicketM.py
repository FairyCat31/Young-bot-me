from disnake.ext import commands
from app.scripts.components.smartdisnake import MEBot
from disnake import ApplicationCommandInteraction, CategoryChannel, PermissionOverwrite, Guild, MessageInteraction
from disnake import Embed, Colour, Member, ButtonStyle
from disnake.ui import Button

MODER_ROLE_IDS = [1271083137211830434, 1223570614993031268, 1220728287941099640]
TICKET_CATEGORY_ID = 1219550920379990056
UNIMICE_GUILD_ID = 1219502611896467476
START_EMBED = Embed(
    description="Выполните процедуры, которые могут помочь с решением вашей проблемы, и если они не помогут подробно опишите свою проблему в одном-двух сообщениях и прикрепите скриншоты. Ваше обращение будет рассмотрено в течение суток!",
    color=Colour.green()
)
START_EMBED.add_field(name="Решение проблем с лаунчером", value="""Данные шаги позволят решить проблемы с лаунчером в 95% случаев:
- Перезапустите пк
- Отключите антивирус
- Включите ВПН
Если данные шаги не помогли - переустановите лаунчер и повторите процедуры
Если даже после переустановки ошибка осталась - напишите в тикете "Процедуры завершены, проблема осталась" и подробно опишите вашу проблему, прикрепив скриншоты.""",
                      inline=False)
START_EMBED.add_field(name="Решение проблем с сервером", value='Проверьте каналы новостей, сервер может находиться на запланированном техническом обслуживании. Если сервер работает - выполните шаги, идентичные шагам в "Ошибки лаунчера" и опишите вашу проблему, описав скриншоты, если процедуры не помогли', inline=False)
CLOSE_TICKET_BTN = Button(custom_id="t_close", label="Закрыть тикет", style=ButtonStyle.red, emoji="✖")

TICKET_OPENER_EMBED = Embed(
    title="Обращения",
    description="При нажатии мы создадим приватный канал для вашего обращения",
    color=Colour.yellow()
)
OPEN_TICKET_BTN = Button(custom_id="t_open", label="Открыть тикет", style=ButtonStyle.green, emoji="💨")
class TicketM(commands.Cog):
    def __init__(self, bot: MEBot):
        self.bot = bot
        self.ticket_category: CategoryChannel | None = None
        self.guild: Guild | None = None
        print(self.guild, self.ticket_category)

    async def open_ticket(self, user_id: int):

        member = self.guild.get_member(user_id)
        overwrites = {
            member: PermissionOverwrite(view_channel=True, embed_links=True, attach_files=True),
            self.guild.default_role: PermissionOverwrite(view_channel=False),
            self.guild.me: PermissionOverwrite(view_channel=True, embed_links=True, attach_files=True)
        }
        for moder_role_id in MODER_ROLE_IDS:
            moder_role = self.guild.get_role(moder_role_id)
            overwrites[moder_role] = PermissionOverwrite(view_channel=True)

        ticket_channel = await self.ticket_category.create_text_channel(f"❗・тикет・{member.global_name}", overwrites=overwrites)
        await ticket_channel.send(embed=START_EMBED, components=[CLOSE_TICKET_BTN])

    async def delete_ticket(self, channel_id: int):
        ticket_channel = self.guild.get_channel(channel_id)
        await ticket_channel.delete()

    @commands.slash_command(name="send_ticket_opener", description="Отправляет сообщение для открытия тикета")
    @commands.default_member_permissions(administrator=True)
    async def send_ticket_opener(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(embed=TICKET_OPENER_EMBED, components=[OPEN_TICKET_BTN])

    @commands.slash_command(name="add_user", description="Добавить участника в тикет")
    async def add_user(self, inter: ApplicationCommandInteraction, member: Member):
        role_check = False
        for role_id in MODER_ROLE_IDS:
            trole = inter.author.get_role(role_id)
            if trole is None:
                continue
            if trole.id == role_id:
                role_check = True
                break
        if not role_check:
            await inter.response.send_message("У вас не хватает полномочий использовать эту команду")
            return
        if inter.channel.category_id != TICKET_CATEGORY_ID:
            await inter.response.send_message("Эту команду можно использовать только в тикете")
            return

        channel = inter.channel
        overwrites = channel.overwrites
        overwrites[member] = PermissionOverwrite(view_channel=True, embed_links=True, attach_files=True)
        await channel.edit(overwrites=overwrites)
        await inter.response.send_message(f"{member.nick} был добавлен в тикет")

    @commands.slash_command(name="close_ticket", description="Закрыть тикет")
    async def close_ticket(self, inter: ApplicationCommandInteraction):
        role_check = False
        for role_id in MODER_ROLE_IDS:
            trole = inter.author.get_role(role_id)
            if trole is None:
                continue
            if trole.id == role_id:
                role_check = True
                break
        if not role_check:
            await inter.response.send_message("У вас не хватает полномочий использовать эту команду")
            return
        if inter.channel.category_id != TICKET_CATEGORY_ID:
            await inter.response.send_message("Эту команду можно использовать только в тикете")
            return

        await inter.channel.delete()

    @commands.Cog.listener()
    async def on_button_click(self, inter: MessageInteraction):
        if inter.component.custom_id not in ["t_close", "t_open"]:
            return

        if inter.component.custom_id == "t_close":
            await inter.channel.delete()
        if inter.component.custom_id == "t_open":
            await self.open_ticket(inter.author.id)
            await inter.response.defer()

    @commands.Cog.listener()
    async def on_ready(self):
        self.ticket_category: CategoryChannel | None = self.bot.get_channel(TICKET_CATEGORY_ID)
        self.guild: Guild = self.bot.get_guild(UNIMICE_GUILD_ID)
        print(self.guild, self.ticket_category)



def setup(bot: MEBot):
    bot.add_cog(TicketM(bot))
