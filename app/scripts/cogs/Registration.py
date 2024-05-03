import asyncio

from disnake import Embed, ModalInteraction, MessageInteraction, CommandInter, ButtonStyle
from disnake.ext import commands
from disnake.ui import Modal, TextInput, Button
# from components.jsonmanager import JsonManager
from components.dbmanager import DatabaseManager
from disnake import TextInputStyle as tis
from asyncio import sleep
from components.smartdisnake import *


class ReadyRegModal(SmartRegModal):
    def __init__(self, cfg: dict, index: int, max_index: int):
        super().__init__(modal_cfg=cfg)
        # self.bls = cfg["button_labels"]
        # self.rcs = cfg["replics"]
        self.index = index
        self.max_index = max_index
        self.user_response = None

    async def callback(self, inter: ModalInteraction):
        user_response = {}
        for key, value in inter.text_values.items():
                user_response[key.capitalize()] = value[:1024]

        self.user_response = user_response

    async def response_member(self, inter: ModalInteraction):
        await inter.response.send_message(
            content=self.cfg["replics"]["reg_command_response"],
            components=[
                Button(label=f"Вы успешно завершили {self.index-1}-ую часть из {self.max_index}",
                       style=ButtonStyle.primary,
                       custom_id="reg_button")
            ]
        )
        return


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_responses = {}
        self.delete_sub_message = {}
        self.cfg = self.bot.cfg
        self.dbm = DatabaseManager("registration.db")
        self.dbm.save_db_init()
        self.dbm.connect()
        self.shape_modals = self.__init_reg_modals()

    def reload(self):
        print("reg перезагружен")

    def __init_reg_modals(self) -> list:
        reg_modal = self.cfg["modals"]["reg_modal"]
        questions = reg_modal["questions"]

        len_questions = len(questions)
        modals = []
        for step_five in range(0, len_questions, 5):
            fields = []
            for step_one_in_five in range(step_five, step_five + 5 if step_five + 5 < len_questions else len_questions):
                field = questions[step_one_in_five]
                fields.append(field)
            modal = {
                "title": "Верификация | Часть {part}",
                "phrase_req_words": "Братик, напиши пожалуйста от {min_words} слов",
                "part": (step_five / 5) + 1,
                "fields": fields
            }

            modals.append(modal)

        return modals

    async def is_have_ids(self, *args):

        for key_discord_el in args:
            if self.bot.cfg["discord_ids"].get(key_discord_el) is None:
                self.bot.log.printf(f"[*/Registration] отмена выполнения ~ {key_discord_el}")
                return False

        return True

    async def auto_moderate(self, inter) -> (bool, str):
        # info = self.user_responses[inter.user.id]

        return True, ""

    async def send_reg_modal(self, inter: MessageInteraction, index: int, max_index: int) -> int:

        modal = ReadyRegModal(cfg=self.shape_modals[index], index=index, max_index=max_index)
        await inter.response.send_modal(modal=modal)

        counter = 0
        while modal.user_response is None:
            await sleep(1)
            counter += 1
            if counter >= 3600:
                return 0

        if type(modal.user_response) != dict:
            return 0

        self.user_responses[inter.user.id] = modal.user_response

        return 1

    async def add_user_to_pending(self, did: int):
        user_data = self.user_responses[did]

    async def func_reg_button(self, inter: MessageInteraction) -> None:
        if not inter.user.get_role(self.cfg["discord_ids"]["player_role"]) is None:
            await inter.response.send_message(content=self.cfg["replics"]["auto_moder_all_ver"], ephemeral=True)
            return

        user_res = self.user_responses.get(inter.author.id)
        if user_res is None:
            user_res = {}

        amount = len(self.shape_modals)
        for index in range(amount - 1):
            # if i find a data from this modal i skip this modal
            if not user_res.get(index) is None:
                continue

            res = await asyncio.wait_for(self.send_reg_modal(inter=inter, index=index, max_index=amount), timeout=9999)

            if index != amount-1 or not res:
                return

        is_accept, reason = await self.auto_moderate(inter=inter)

        if not is_accept:
            del self.user_responses[inter.user.id]
            await inter.response.send_message(content=reason)
            return

        await self.add_user_to_pending(did=inter.user.id)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def reg(self, inter: CommandInter):
        # print(self.shape_modals)
        # await inter.response.send_message("ok")
        res = await self.is_have_ids("ver_result_ch")
        if not res:
            inter.response.defer()
            return

        await inter.response.send_message(
            content=self.cfg["replics"]["reg_command_response"],
            components=[
                Button(label=self.cfg["button_labels"]["reg_start"], style=ButtonStyle.success, custom_id="reg_button"),
            ],
        )


        '''
        
        "title": "Верификация | Часть {part}",
        "phrase_req_words": "Братик, напиши пожалуйста от {min_words} слов",
        
        {
            "part": int,
            "title": "str",
            "phrase_req_words": "Братик, напиши пожалуйста от {min_words} слов"
            "fields" : [
            {         
                    "question": "str 45 characters",
                    "data_type": "str/int/(custom)",
                    "custom_id": "str",
                    "style": "long / short *optional"
                    "min_words": "int *optional"
            }
            ]

        }

        '''

    @commands.Cog.listener()
    async def on_button_click(self, inter: MessageInteraction):
        res = await self.is_have_ids("ver_result_ch")
        if not res:
            inter.response.defer()
            return

        if inter.component.custom_id not in ["reg_button"]:
            # We filter out any other button presses except
            # the components we wish to process.
            return

        if inter.component.custom_id == "reg_button":
            await self.func_reg_button(inter=inter)

        # if inter.component.custom_id == "user_modal_button":
        #     m_reg = RegModal(cfg=self.cfg)
        #     await inter.response.send_modal(modal=m_reg)
        #
        #     while True:
        #         await sleep(0.5)
        #         if m_reg.user_response:
        #             self.user_responses[str(inter.user.id)] = {}
        #             self.user_responses[str(inter.user.id)]["user_data"] = m_reg.user_response
        #             break
        #
        #     return
        #
        # elif inter.component.custom_id == "game_modal_button":
        #     g_reg = GameModal(cfg=self.cfg)
        #     await inter.response.send_modal(modal=g_reg)
        #
        #     while True:
        #         await sleep(0.5)
        #         if g_reg.user_response:
        #             self.user_responses[str(inter.user.id)]["game_data"] = g_reg.user_response
        #             break
        #
        #     self.user_responses[str(inter.user.id)]["result"] = {}
        #     for key, value in self.user_responses[str(inter.user.id)]["user_data"].items():
        #         self.user_responses[str(inter.user.id)]["result"][key] = value
        #     for key, value in self.user_responses[str(inter.user.id)]["game_data"].items():
        #         self.user_responses[str(inter.user.id)]["result"][key] = value
        #
        #
        #
        #     if not is_accept:
        #         embed = SmartEmbed(cfg=self.cfg["embeds"]["request_reject"])
        #         embed.title = self.cfg["embeds"]["request_reject"]["title"].format(user_name=inter.user.name)
        #         embed.add_field(
        #             name=self.cfg["embeds"]["request_reject"]["other"]["field"]["name"],
        #             value=self.cfg["embeds"]["request_reject"]["other"]["field"]["value"].format(reason=reason),
        #             inline=self.cfg["embeds"]["request_reject"]["other"]["field"]["inline"],
        #             )
        #
        #         await self.bot.get_channel(self.bot.cfg["discord_ids"]["ver_result_ch"]).send(content=inter.user.mention, embed=embed) # результаты верифа
        #         return
        #
        #     self.dbm.user_add(table="PendingUsers", discord_id=inter.user.id, ud=self.user_responses[str(inter.user.id)]["result"])
        #     self.dbm.commit()


def setup(bot: commands.Bot):
    bot.add_cog(Registration(bot))