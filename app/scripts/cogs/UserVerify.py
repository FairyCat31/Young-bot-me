from disnake.ext import commands
from app.scripts.components.smartdisnake import MEBot
from disnake import ApplicationCommandInteraction
from disnake import Embed, Colour, Member


UNIMICE_ROLE_ID = 1219532060608299079
CHANNEL_INFO_ID = 1230932637657600111


class UserVerify(commands.Cog):
    def __init__(self, bot: MEBot):
        self.bot = bot

    @commands.slash_command(name="ver_users", description="Добавляет в список игроков")
    @commands.default_member_permissions(administrator=True)
    async def verify(self, inter: ApplicationCommandInteraction, names: str):
        result = ""
        await inter.response.send_message("Обрабатываем запрос")
        channel = inter.channel
        for name in names.split(" "):
            if not name:
                continue
            name = name.strip()
            user: Member = inter.guild.get_member(int(name)) if name.isdigit() else inter.guild.get_member_named(name)
            if user is None:
                result += f"{name} ❌ Игрок не найден\n"
                continue
            temp_embed = Embed(title=f"ЗАЯВКА {user.name}", colour=Colour.green())
            temp_embed.add_field(name="Статус заявки", value="Принята", inline=False)
            temp_embed.add_field(name="Информация", value="Выбери сервер в канале <#1267790201909153854>\nЗатем скачайте Java FX и Лаунчер в канале <#1219551109304156160>\nУдачи тебе, игрок)", inline=False)
            player_role = inter.guild.get_role(UNIMICE_ROLE_ID)
            await user.add_roles(player_role)
            ch = inter.guild.get_channel(CHANNEL_INFO_ID)
            await ch.send(content=f"{user.mention}", embed=temp_embed)
            result += f"{user.name} ✅ Игрок был одобрен\n"
        await channel.send(result)


def setup(bot: MEBot):
    bot.add_cog(UserVerify(bot))
