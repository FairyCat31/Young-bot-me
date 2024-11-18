import sqlite3
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Connection
from app.scripts.components.jsonmanager import JsonManagerWithCrypt, AddressType
from sqlalchemy import (
    MetaData
)


CONNECT_SHAPE_URL_MARIADB = "mariadb+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
CONNECT_SHAPE_URL_SQLITE3 = "app/data/local_dbs/{db_name}.db"


def get_url_by_dict(data_for_conn: dict) -> str:
    conn_address = data_for_conn["CONN_URL"].format(
        DB_USER=data_for_conn["DB_USER"],
        DB_PASS=data_for_conn["DB_PASS"],
        DB_HOST=data_for_conn["DB_HOST"],
        DB_PORT=data_for_conn["DB_PORT"],
        DB_NAME=data_for_conn["DB_NAME"]
    )
    return conn_address


class DBType:
    """

    """
    MariaDB = CONNECT_SHAPE_URL_MARIADB
    SQLite3 = CONNECT_SHAPE_URL_SQLITE3


class DBManager:
    """
    Basic manager for raw interact with db

    Without models and tables shapes
    """
    def __init__(self, database_name: str, db_type: str, echo: bool = False):
        self._db_name = database_name
        # load crypt json which content data for connect to database
        self._json_manager = JsonManagerWithCrypt(AddressType.CFILE, ".dbs.crptjson")
        self._json_manager.load_from_file()
        # get data for connect to database by name which set in param database_name
        # structure of dict {
        # "DB_HOST": STR
        # "DB_PORT": INT
        # "DB_USER": STR
        # "DB_PASS": STR
        # "DB_NAME": STR
        data_for_conn: dict = self._json_manager.get_buffer().get(database_name)
        data_for_conn["CONN_URL"] = db_type
        self.engine = create_engine(url=get_url_by_dict(data_for_conn), echo=echo, pool_size=5, max_overflow=10,)
        self.metadata_obj = MetaData()

    @staticmethod
    def db_connect(func):
        """
        Decorator for func, which work with db
        """
        def wrapper(self, *args, **kwargs):
            with self.engine.connect() as conn:
                func(self, conn, *args, **kwargs)

        return wrapper

    @db_connect
    def create_tables(self, conn: Connection):
        self.metadata_obj.create_all(conn)
        conn.commit()

    @db_connect
    def drop_tables(self, conn: Connection):
        self.metadata_obj.drop_all(conn)
        conn.commit()


class LiteDBManager:
    def __init__(self, db_path: str):
        self._db_path = db_path

    @staticmethod
    def db_connect(func):
        def wrapper(self, *args, **kwargs):
            with sqlite3.connect(self._db_path) as conn:
                res = func(self, conn, *args, **kwargs)
                return res
        return wrapper
