import sqlite3
from os.path import exists, dirname
from os import makedirs


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
        self.cursor.execute(f'SELECT did, login, name, gender, old, desc, way, inter, move, skill, soc FROM {table}')
        ids = self.cursor.fetchall()
        return ids

    def user_add(self, table: str, ud: dict, discord_id: int):
        self.cursor.execute(
            f"INSERT INTO {table} (did, login, name, gender, old, desc, way, inter, move, skill, soc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (discord_id, ud["ilogin"], ud["iname"], ud["igender"], ud["iold"], ud["idesc"], ud["iway"], ud["iinter"], ud["imove"], ud["iskill"], ud["isoc"])
             )

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

        if not result:
            makedirs(dirname(self.file_path), exist_ok=True)

        self.connection = sqlite3.connect(self.file_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS PendingUsers (
        id INTEGER PRIMARY KEY,
        did INTEGER,
        login TEXT NOT NULL,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        old TEXT NOT NULL,
        desc TEXT NOT NULL,
        way TEXT NOT NULL,
        inter TEXT NOT NULL,
        move TEXT NOT NULL,
        skill TEXT NOT NULL,
        soc TEXT NOT NULL
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS AcceptedUsers (
        id INTEGER PRIMARY KEY,
        did INTEGER,
        login TEXT NOT NULL,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        old TEXT NOT NULL,
        desc TEXT NOT NULL,
        way TEXT NOT NULL,
        inter TEXT NOT NULL,
        move TEXT NOT NULL,
        skill TEXT NOT NULL,
        soc TEXT NOT NULL
        )
        ''')
        self.connection.commit()
        self.connection.close()