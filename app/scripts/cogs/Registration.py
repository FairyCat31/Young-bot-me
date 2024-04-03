import disnake
from disnake.ext import commands
from disnake.ui import Modal, TextInput
# from components.jsonmanager import JsonManager
from components.dbmanager import DatabaseManager
from disnake import TextInputStyle as tis
from asyncio import sleep


class SmartModal(Modal):
    def __init__(self, cfg: dict):
        self.cfg = cfg
        components = [
            TextInput(
                label=ti["label"],
                placeholder=ti["placeholder"],
                max_length=ti["max_length"],
                min_length=ti["min_length"],
                required=ti["required"],
                custom_id=ti["custom_id"],
                style=tis.long if ti["style"] == "long" else tis.short
        ) for ti in cfg["text_inputs"]
        ]
        super().__init__(title=cfg["title"], custom_id=cfg["custom_id"], components=components)
        # "label": "\uD83E\uDDD1\u200D\uD83D\uDCBB Игровой никнейм (логин на [сайте](https://mousearth.ru/))",
        # "placeholder": "_pyth",
        # "max_length": 25,
        # "min_length": 5,
        # "required": true,j
        # "style": "short"

        # "title" : "\uD83D\uDCC7 Верификация | Личная информация \uD83D\uDCBB",
        # "custom_id": "ipers",

    async def callback(self, inter):
        pass


class RegModal(SmartModal):
    def __init__(self, cfg: dict):
        super().__init__(cfg=cfg["pers_info"])
        self.cfg = cfg
        self.user_response = None

    async def callback(self, inter: disnake.ModalInteraction):

        self.user_response = inter.text_values

        await inter.response.send_message(
            f"{inter.user.mention} пройдите вторую часть регистрации",
            ephemeral=True,
            components=[
                disnake.ui.Button(label="Продолжить", style=disnake.ButtonStyle.primary, custom_id="game_modal_button")
            ],
        )


class GameModal(SmartModal):
    def __init__(self, cfg: dict):
        self.cfg = cfg
        # print(self.cfg)
        super().__init__(cfg=self.cfg["gameplay"])
        self.user_response = None
        self.last_mess_response = 0

    async def callback(self, inter: disnake.ModalInteraction):

        embed = disnake.Embed(title=f"Заявка {inter.user.name}")

        embed.add_field(
            name="Стадия заявки",
            value="Заявка проходит модерацию",
            inline=False,
            )

        await inter.response.send_message(content=inter.user.mention, embed=embed, ephemeral=True)
        self.user_response = inter.text_values


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_responses = {}
        self.delete_sub_message = {}
        self.cfg = self.bot.cfg.buffer[bot.name]["modals"]
        self.dbm = DatabaseManager("registration.db")
        self.dbm.save_db_init()
        self.dbm.connect()

    async def auto_moderate(self, inter) -> (bool, str):
        info = self.user_responses[str(inter.user.id)]["result"]
        try:
            int(info["iold"])
        except ValueError:
            return False, "Неверный формат возраста"

        if info["igender"] not in ["м", "ж", "д", "М", "Ж", "Д"]:
            return False, "Неверный формат пола"

        if inter.user.get_role(1224805920140300389):
            return False, "Вы уже авторизованы"

        return True, ""

    @commands.slash_command()
    async def reg(self, inter: disnake.CommandInter):

        await inter.response.send_message(
            "Чтобы пройти верификацию, нажмите кнопку ниже",
            components=[
                disnake.ui.Button(label="Пройти", style=disnake.ButtonStyle.success, custom_id="user_modal_button"),
            ],
        )

    @commands.Cog.listener(name="on_button_click")
    async def when_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in ["game_modal_button", "user_modal_button"]:
            # We filter out any other button presses except
            # the components we wish to process.
            return

        if inter.component.custom_id == "user_modal_button":
            m_reg = RegModal(cfg=self.cfg)
            await inter.response.send_modal(modal=m_reg)

            while True:
                await sleep(0.5)
                if m_reg.user_response:
                    self.user_responses[str(inter.user.id)] = {}
                    self.user_responses[str(inter.user.id)]["user_data"] = m_reg.user_response
                    break

            return

        elif inter.component.custom_id == "game_modal_button":
            g_reg = GameModal(cfg=self.cfg)
            await inter.response.send_modal(modal=g_reg)

            while True:
                await sleep(0.5)
                if g_reg.user_response:
                    self.user_responses[str(inter.user.id)]["game_data"] = g_reg.user_response
                    mess_id_to_edit = g_reg.last_mess_response
                    break
            # print(self.user_responses[str(inter.user.id)])

            # json_manager = JsonManager()
            # json_manager.dload_cfg(short_name="pending_user.json")

            self.user_responses[str(inter.user.id)]["result"] = {}
            for key, value in self.user_responses[str(inter.user.id)]["user_data"].items():
                self.user_responses[str(inter.user.id)]["result"][key] = value
            for key, value in self.user_responses[str(inter.user.id)]["game_data"].items():
                self.user_responses[str(inter.user.id)]["result"][key] = value

            is_accept, reason = await self.auto_moderate(inter=inter)

            if not is_accept:
                embed = disnake.Embed(title=f"Заявка {inter.user.name}", description="Ваша заявка отклонена")
                embed.add_field(
                    name="Причина",
                    value=reason,
                    inline=False,
                    )

                await self.bot.get_channel(1224426633767817236).send(content=inter.user.mention, embed=embed)
                return

            self.dbm.user_add(table="PendingUsers", discord_id=inter.user.id, ud=self.user_responses[str(inter.user.id)]["result"])
            self.dbm.commit()


def setup(bot: commands.Bot):
    bot.add_cog(Registration(bot))