import sqlite3
from os.path import exists, dirname
from os import makedirs
from components.jsonmanager import JsonManager

_default_path = "data/dbs/"


class DatabaseManager:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file_path = _default_path + self.file_name
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.file_path)
        self.cursor = self.connection.cursor()

    def custom_execute(self, sql_command: str, **kwargs):
        self.cursor.execute(sql_command, **kwargs)

    def user_get(self, table: str, discord_id: int) -> dict:
        self.cursor.execute(f'SELECT login, name, gender, old, desc, way, inter, move, skill, soc FROM {table} WHERE did = ?', (discord_id,))
        results = self.cursor.fetchall()
        ud = {}
        keys = ["ilogin", "iname", "igender", "iold", "idesc", "iway", "iinter", "imove", "iskill", "isoc"]
        for i in range(len(results[0])):
            ud[keys[i]] = results[0][i]

        return ud

    def users_get_id(self, table: str) -> tuple:
        jsm = JsonManager()
        jsm.dload_cfg("bots_properties.json")
        fields = jsm.buffer["YoungMouse"]["modals"]["reg_modal"]["questions"]
        db_field = "did, " + ", ".join(field["custom_id"] for field in fields)
        self.cursor.execute(f'SELECT {db_field} FROM {table}')
        ids = self.cursor.fetchall()
        return ids

    def user_add(self, table: str, ud: dict, discord_id: int):
        db_keys = "did"
        db_qm = "?"
        values = [discord_id]
        for key in ud.keys():
            db_keys += f", {key}"
            db_qm += ", ?"
            values.append(ud[key]["value"])

        self.cursor.execute(f"INSERT INTO {table} ({db_keys}) VALUES ({db_qm})", tuple(values))

    def user_add_2(self, table: str, ud: dict):
        db_keys = ""
        db_qm = ""
        values = []
        for key in ud.keys():
            db_keys += f", {key}" if db_keys else key
            db_qm += ", ?" if db_qm else "?"
            values.append(ud[key])

        self.cursor.execute(f"INSERT INTO {table} ({db_keys}) VALUES ({db_qm})", tuple(values))

    def user_delete(self, table: str, discord_id: int):
        self.cursor.execute(f'DELETE FROM {table} WHERE did = ?', (discord_id,))

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.commit()
        self.connection.close()

        self.connection = None
        self.cursor = None

    def save_db_init(self):
        result = exists(self.file_path)
        jsm = JsonManager()
        jsm.dload_cfg("bots_properties.json")
        if not result:
            makedirs(dirname(self.file_path), exist_ok=True)

        fields = jsm.buffer["YoungMouse"]["modals"]["reg_modal"]["questions"]
        db_field = [field["custom_id"] for field in fields]
        field_prompt = "id INTEGER PRIMARY KEY, did INTEGER"
        for field in db_field:
            field_prompt += f", {field} TEXT NOT NULL"

        self.connection = sqlite3.connect(self.file_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS PendingUsers ({field_prompt})')
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS AcceptedUsers ({field_prompt})')
        self.connection.commit()
        self.connection.close()