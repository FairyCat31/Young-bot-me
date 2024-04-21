from disnake import Embed, ModalInteraction, MessageInteraction, CommandInter, ButtonStyle
from disnake.ext import commands
from disnake.ui import Modal, TextInput, Button
# from components.jsonmanager import JsonManager
from components.dbmanager import DatabaseManager
from disnake import TextInputStyle as tis
from asyncio import sleep
from components.smartdisnake import *


class RegModal(SmartModal):
    def __init__(self, cfg: dict):
        super().__init__(modal_cfg=cfg["modals"]["pers_info"])
        self.bls = cfg["button_labels"]
        self.rcs = cfg["replics"]
        self.user_response = None

    async def callback(self, inter: ModalInteraction):

        self.user_response = inter.text_values

        await inter.response.send_message(
            self.rcs["reg_modal_response_2"].format(user_mention=inter.user.mention),
            ephemeral=True,
            components=[
                Button(label=self.bls["next"], style=ButtonStyle.primary, custom_id="game_modal_button")
            ],
        )


class GameModal(SmartModal):
    def __init__(self, cfg: dict):
        self.cfg = cfg
        # print(self.cfg)
        super().__init__(modal_cfg=self.cfg["modals"]["gameplay"])
        self.user_response = None

    async def callback(self, inter: ModalInteraction):
        embed = SmartEmbed(cfg=self.cfg["embeds"]["game_modal_callback"])
        embed.title = embed.title.format(user_name=inter.user.name)

        await inter.response.send_message(content=inter.user.mention, embed=embed, ephemeral=True)
        self.user_response = inter.text_values


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_responses = {}
        self.delete_sub_message = {}
        self.cfg = self.bot.cfg
        self.dbm = DatabaseManager("registration.db")
        self.dbm.save_db_init()
        self.dbm.connect()

    def reload(self):
        print("reg перезагружен")

    async def is_have_ids(self, *args):

        for key_discord_el in args:
            if self.bot.cfg["discord_ids"].get(key_discord_el) is None:
                self.bot.log.printf(f"[*/Registration] отмена выполнения ~ {key_discord_el}")
                return False

        return True

    async def auto_moderate(self, inter) -> (bool, str):
        info = self.user_responses[str(inter.user.id)]["result"]
        try:
            int(info["iold"])
            if int(info["iold"]) < 1:
                return False, self.cfg["replics"]["auto_moder_wr_old_ft"]
        except ValueError:
            return False, self.cfg["replics"]["auto_moder_wr_old_ft"]

        if info["igender"] not in self.cfg["genders"]:
            return False, self.cfg["replics"]["auto_moder_wr_gender_ft"]

        if inter.user.get_role(self.bot.cfg["discord_ids"]["player_role"]):  # роль игрока
            return False, self.cfg["replics"]["auto_moder_all_ver"]

        return True, ""

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def reg(self, inter: CommandInter):
        res = await self.is_have_ids("ver_result_ch")
        if not res:
            inter.response.defer()
            return

        await inter.response.send_message(
            content=self.cfg["replics"]["reg_command_response"],
            components=[
                Button(label=self.cfg["button_labels"]["reg_start"], style=ButtonStyle.success, custom_id="user_modal_button"),
            ],
        )

    @commands.Cog.listener(name="on_button_click")
    async def when_button_click(self, inter: MessageInteraction):
        res = await self.is_have_ids("ver_result_ch")
        if not res:
            inter.response.defer()
            return

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
                    break

            self.user_responses[str(inter.user.id)]["result"] = {}
            for key, value in self.user_responses[str(inter.user.id)]["user_data"].items():
                self.user_responses[str(inter.user.id)]["result"][key] = value
            for key, value in self.user_responses[str(inter.user.id)]["game_data"].items():
                self.user_responses[str(inter.user.id)]["result"][key] = value

            is_accept, reason = await self.auto_moderate(inter=inter)

            if not is_accept:
                embed = SmartEmbed(cfg=self.cfg["embeds"]["request_reject"])
                embed.title = self.cfg["embeds"]["request_reject"]["title"].format(user_name=inter.user.name)
                embed.add_field(
                    name=self.cfg["embeds"]["request_reject"]["other"]["field"]["name"],
                    value=self.cfg["embeds"]["request_reject"]["other"]["field"]["value"].format(reason=reason),
                    inline=self.cfg["embeds"]["request_reject"]["other"]["field"]["inline"],
                    )

                await self.bot.get_channel(self.bot.cfg["discord_ids"]["ver_result_ch"]).send(content=inter.user.mention, embed=embed) # результаты верифа
                return

            self.dbm.user_add(table="PendingUsers", discord_id=inter.user.id, ud=self.user_responses[str(inter.user.id)]["result"])
            self.dbm.commit()


def setup(bot: commands.Bot):
    bot.add_cog(Registration(bot))