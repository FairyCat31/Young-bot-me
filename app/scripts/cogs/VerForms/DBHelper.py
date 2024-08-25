from app.scripts.components.dbmanager.dbmanager import DBManager, DBType
from app.scripts.components.dbmanager import db_data_types
from sqlalchemy.engine.base import Connection
from sqlalchemy import Table, Column
from typing import Dict, List
from sqlalchemy import insert, delete, select


class PendingDBManager(DBManager):
    """
    manager with engine, model, model.table for raw interation with PendingUsersTable
    """
    def __init__(self, reg_fields_list: List[Dict], name: str = "registration", db_type: str = DBType.MariaDB):
        super().__init__(database_name=name, db_type=db_type)
        self._columns = self.__column_init(reg_fields_list)
        self.pending_table = Table("PendingUsers", self.metadata_obj, *self._columns)

    """
            Convert List of [
            {
                    "question": "Ваш логин на сайте?",
                    "data_type": "str_20",
                    "custom_id": "login",
                    "example": "test"
                }, ...]
            to
            [Column("login", String(20)]
        """

    @staticmethod
    def __column_init(reg_fields_list: List[Dict]) -> List[Column]:
        map_types = db_data_types.map_types
        columns = [Column("id", map_types["int"], primary_key=True),
                   Column("did", map_types["int_big"])]

        for reg_field in reg_fields_list:
            field_name = reg_field["classic"]["custom_id"]
            map_types.setdefault(reg_field["data_type"], map_types["str"])
            data_type = map_types[reg_field["data_type"]]

            columns.append(Column(field_name, data_type))

        return columns

    # func for add user to pending table
    @DBManager.db_connect
    def insert_to_pending_table(self, conn: Connection, user_data: dict):
        # generate sql statement
        stmt = (
            insert(self.pending_table).
            values(**user_data)
        )
        # execute stmt and commit changes
        conn.execute(stmt)
        conn.commit()


class AcceptedDBManager(PendingDBManager):
    """
    manager with engine, model, model.table for raw interation with PendingUsersTable
    """
    def __init__(self, reg_fields_list: List[Dict], name: str = "registration", db_type: str = DBType.MariaDB):
        super().__init__(reg_fields_list=reg_fields_list, name=name, db_type=db_type)
        self.accepted_table = Table("AcceptedUsers", self.metadata_obj, *self._columns)

    @DBManager.db_connect
    def insert_to_accepted_table(self, conn: Connection, user_data: dict):
        # generate sql statement
        stmt = (
            insert(self.accepted_table).
            values(**user_data)
        )
        # execute stmt and commit changes
        conn.execute(stmt)
        conn.commit()

    @DBManager.db_connect
    def get_all_from_pending_table(self, conn: Connection):
        # generate sql statement
        stmt = (
            select(self.pending_table)
        )
        # execute stmt and commit changes
        output = conn.execute(stmt)
        print(output)

    @DBManager.db_connect
    def delete_from_pending_table(self, conn: Connection, did: int):
        # generate sql statement
        stmt = (
            delete(self.pending_table).
            where(self.pending_table.c.did == did)
        )
        # execute stmt and commit changes
        conn.execute(stmt)
        conn.commit()
