from disnake.ext import commands
from app.scripts.components.smartdisnake import MEBot
from disnake import ApplicationCommandInteraction
from disnake import Embed, Colour


UNIMICE_ROLE_ID = 1219532060608299079
CHANNEL_INFO_ID = 1230932637657600111


class UserVerify(commands.Cog):
    def __init__(self, bot: MEBot):
        self.bot = bot

    @commands.slash_command(name="ver_user", description="Добавляет в список игроков")
    @commands.default_member_permissions(administrator=True)
    async def verify(self, inter: ApplicationCommandInteraction, name: str):
        user = inter.guild.get_member_named(name)
        temp_embed = Embed(title=f"ЗАЯВКА {name}", colour=Colour.green())
        temp_embed.add_field(name="Статус заявки", value="Принята", inline=False)
        temp_embed.add_field(name="Информация", value="Выбери сервер в канале <#1267790201909153854>\nЗатем скачайте Java FX и Лаунчер в канале <#1219551109304156160>\nУдачи тебе, игрок)", inline=False)
        player_role = inter.guild.get_role(UNIMICE_ROLE_ID)
        if user is None:
            await inter.response.send_message(f"Игрок с ником {name} не найден")
            return
        await user.add_roles(player_role)
        ch = inter.guild.get_channel(CHANNEL_INFO_ID)
        await ch.send(content=f"{user.mention}", embed=temp_embed)
        await inter.response.send_message("Всё ок ✅")


def setup(bot: MEBot):
    bot.add_cog(UserVerify(bot))
