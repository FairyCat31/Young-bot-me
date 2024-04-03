from bot_manager import BotManager
from components.dbmanager import DatabaseManager


# dbm = DatabaseManager(file_name="registration.db")
# dbm.connect()
# #dbm.user_get(table="PendingUsers", discord_id=642080060093890599)
# print(dbm.users_get_id(table="PendingUsers"))

bman = BotManager()
bman.init_bot(name_bot="YoungMouse")