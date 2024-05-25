import asyncio
from datetime import datetime
from disnake import Embed, ModalInteraction, MessageInteraction, CommandInter, ButtonStyle
from disnake.ext import commands
from disnake.ui import Modal, TextInput, Button
# from components.jsonmanager import JsonManager
from components.dbmanager import DatabaseManager
from disnake import TextInputStyle as tis
from asyncio import sleep
from components.smartdisnake import *


class ReadyRegModal(SmartRegModal):
    def __init__(self, cfg: dict, bot, index: int, max_index: int):
        super().__init__(modal_cfg=cfg)
        self.bot = bot
        # self.bls = cfg["button_labels"]
        # self.rcs = cfg["replics"]
        self.index = index
        self.max_index = max_index
        self.user_response = None

    async def callback(self, inter: ModalInteraction):
        user_response = {}
        fields = self.modal_cfg["fields"]
        for index, key_value in enumerate(inter.text_values.items()):
            key, value = key_value
            data_type, min_words = fields[index]["data_type"], fields[index].get("min_words")
            response_to_question = {
                "value": value[:1024],
                "data_type": data_type,
                "min_words": 0 if min_words is None else min_words
            }
            user_response[key] = response_to_question
        self.user_response = user_response
        await self.response_member(inter=inter)

    async def response_member(self, inter: ModalInteraction):
        if self.index+1 != self.max_index:
            await inter.response.send_message(
                content=self.bot.cfg["replics"]["reg_modal_response"].format(index=self.index+1, max_index=self.max_index),
                components=[
                    Button(label="Продолжить",
                           style=ButtonStyle.primary,
                           emoji="🔹",
                           custom_id="reg_button")
                ],
                ephemeral=True
            )
            return

        await inter.response.send_message(
            self.bot.cfg["replics"]["ver_response"],
            ephemeral=True
        )


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_responses = {}
        self.delete_sub_message = {}
        self.cfg = bot.cfg
        self.log = bot.log
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
                "title": reg_modal["title"],
                "phrase_req_words": reg_modal["phrase_req_words"],
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

    async def check_dt_str(self, value: str) -> bool:
        return True

    async def check_dt_int(self, value: str) -> bool:
        return value.isdigit()

    async def check_dt_date(self, value: str) -> bool:
        for s in " .,/":
            t = value.split(s)
            l = len(t)

            if l != 3:
                continue
            # len = 3
            for v in t:
                if not v.isdigit():
                    return False
            # [int, int, int]
            return True
            # ["qd", "wer", '12342']

    async def check_dt_gender(self, value: str) -> bool:
        if len(value) != 1:
            return False

        return value in ["м", "М", "д", "Д", "ж", "Ж"]

    async def auto_moderate(self, inter) -> (bool, str):
        data_type_func = {
            "str": self.check_dt_str,
            "int": self.check_dt_int,
            "date": self.check_dt_date,
            "gender": self.check_dt_gender
        }

        user_data = self.user_responses[inter.user.id]["full"]
        for key in user_data.keys():
            value = user_data[key]['value']
            data_type = user_data[key]['data_type']
            min_words = user_data[key]['min_words']

            if not await asyncio.wait_for(data_type_func[data_type](value=value), timeout=10):
                return False, f"Вы неверно указали данные({value}) в поле {value}"

            len_text = len(value.split(" "))
            if len_text < min_words:
                return False, f"Пункт {key} слишком короткий\nВы написали {len_text} слов, а надо минимум {min_words}"

        return True, ""

    async def send_reg_modal(self, inter: MessageInteraction, bot, index: int, max_index: int) -> int:

        modal = ReadyRegModal(cfg=self.shape_modals[index], bot=bot, index=index, max_index=max_index)
        await inter.response.send_modal(modal=modal)

        counter = 0
        while modal.user_response is None:
            await sleep(1)
            counter += 1
            if counter >= 3600:
                return 0

        if type(modal.user_response) != dict:
            return 0

        if self.user_responses.get(inter.user.id) is None:
            self.user_responses[inter.user.id] = {}

        self.user_responses[inter.user.id][index] = modal.user_response

        return 1

    async def func_reg_button(self, inter: MessageInteraction) -> None:
        if not inter.user.get_role(self.cfg["discord_ids"]["player_role"]) is None:
            await inter.response.send_message(content=self.cfg["replics"]["auto_moder_all_ver"], ephemeral=True)
            return

        user_res = self.user_responses.get(inter.author.id)
        if user_res is None:
            user_res = {}

        amount = len(self.shape_modals)
        for index in range(amount):
            # if i find a data from this modal i skip this modal
            if not user_res.get(index) is None:
                continue

            res = await asyncio.wait_for(self.send_reg_modal(inter=inter, bot=self.bot, index=index, max_index=amount), timeout=9999)

            if index != amount-1 or not res:
                return

        user_response = self.user_responses[inter.user.id]
        keys = list(user_response.keys())
        self.user_responses[inter.user.id]["full"] = {}
        for part_key in keys:
            for answer_key in user_response[part_key]:
                 self.user_responses[inter.user.id]["full"][answer_key] = user_response[part_key][answer_key]

        is_accept, reason = await asyncio.wait_for(self.auto_moderate(inter=inter), timeout=100)

        if not is_accept:
            del self.user_responses[inter.user.id]
            self.log.printf(f"[*/Registration] участник({inter.user.global_name}) не пропущен\n{reason}")
            await inter.channel.send(content=reason)
            return

        self.log.printf(f"[*/Registration] игрок({inter.user.global_name}) подал заявку")
        self.dbm.user_add(table="PendingUsers", ud=self.user_responses[inter.user.id]["full"], discord_id=inter.user.id)
        self.dbm.commit()
        del self.user_responses[inter.user.id]

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

    @commands.Cog.listener()
    async def on_button_click(self, inter: MessageInteraction):
        res = await self.is_have_ids("ver_result_ch")
        if not res:
            await inter.response.defer()
            return

        if inter.component.custom_id not in ["reg_button"]:
            # We filter out any other button presses except
            # the components we wish to process.
            return

        if inter.component.custom_id == "reg_button":
            await self.func_reg_button(inter=inter)


def setup(bot: commands.Bot):
    bot.add_cog(Registration(bot))