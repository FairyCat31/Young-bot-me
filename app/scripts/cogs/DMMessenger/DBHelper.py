from app.scripts.components.dbmanager.dbmanager import LiteDBManager, DBType
import sqlite3


class SQLRequests:
    CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS user_dm (
id INTEGER PRIMARY KEY,
uid INTEGER NOT NULL,
ch_id INTEGER NOT NULL
)
'''
    ADD_USER_AND_DM = 'INSERT INTO user_dm (uid, ch_id) VALUES (?, ?)'
    GET_USER = 'SELECT uid FROM user_dm WHERE ch_id = ?'
    GET_DM = 'SELECT ch_id FROM user_dm WHERE uid = ?'
    DEL_BY_UID = 'DELETE FROM user_dm WHERE uid = ?'
    DEL_BY_CHID = 'DELETE FROM user_dm WHERE ch_id = ?'
    BLOCK_USER = 'UPDATE user_dm SET ch_id = ? WHERE uid = ?'


class DBManagerForDM(LiteDBManager):
    def __init__(self, db_name: str = "dm_user_messenger"):
        super().__init__(DBType.SQLite3.format(db_name=db_name))

    @LiteDBManager.db_connect
    def save_start(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        cursor.execute(SQLRequests.CREATE_TABLE)
        conn.commit()

    @LiteDBManager.db_connect
    def get_user_id(self, conn: sqlite3.Connection, ch_id: int) -> int:
        cursor = conn.cursor()
        cursor.execute(SQLRequests.GET_USER, (ch_id,))
        output = cursor.fetchone()
        result = 0 if output is None else output[0]
        return result

    @LiteDBManager.db_connect
    def get_dm_id(self, conn: sqlite3.Connection, uid: int) -> int:
        cursor = conn.cursor()
        cursor.execute(SQLRequests.GET_DM, (uid,))
        output = cursor.fetchone()
        if output is None:
            result = 0
        else:
            result = output[0]
        return result

    @LiteDBManager.db_connect
    def add_user_and_dm(self, conn: sqlite3.Connection, uid: int, ch_id: int) -> None:
        cursor = conn.cursor()
        cursor.execute(SQLRequests.ADD_USER_AND_DM, (uid, ch_id,))
        conn.commit()

    @LiteDBManager.db_connect
    def del_user_and_dm(self, conn: sqlite3.Connection, uid: int) -> None:
        cursor = conn.cursor()
        cursor.execute(SQLRequests.DEL_BY_UID, (uid,))
        conn.commit()

    @LiteDBManager.db_connect
    def del_user_and_dm_by_chid(self, conn: sqlite3.Connection, ch_id: int) -> None:
        cursor = conn.cursor()
        cursor.execute(SQLRequests.DEL_BY_CHID, (ch_id, ))
        conn.commit()

    @LiteDBManager.db_connect
    def block_or_unblock_user(self, conn: sqlite3.Connection, uid: int, block: bool = None, unblock: bool = None):
        cursor = conn.cursor()
        dm_id = self.get_dm_id(uid)
        if block:
            dm_id = dm_id * -1 if dm_id > 0 else dm_id
        elif unblock:
            dm_id = dm_id if dm_id > 0 else dm_id * -1
        else:
            dm_id *= -1
        cursor.execute(SQLRequests.BLOCK_USER, (dm_id, uid))
        conn.commit()
