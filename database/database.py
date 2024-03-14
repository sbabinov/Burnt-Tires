from __future__ import annotations

import os
import sys
import json
import pickle
import inspect
from sqlite3 import connect

from .tables import *


class Database:
    __database_path = './main.db'
    __tables_module = 'database.tables'
    __table_data_path = 'database/data/'
    __available_types = [INT, REAL, TEXT, LIST]
    __tables = dict()


    @staticmethod
    def __load_table_data(path: str) -> Dict | None:
        try:
            with open(path, 'r') as td:
                table_data = json.load(td)
                for table_name in table_data:
                    fields = table_data[table_name]['fields']
                    for field in fields:
                        fields[field] = STR_TYPES[fields[field]]
        except FileNotFoundError:
            table_data = None
        except EOFError:
            table_data = None
        return table_data

    @staticmethod
    def __get_td_path() -> str:
        return os.path.join(Database.__table_data_path, 'table_data.json')

    def __create_table(self, table) -> Table:
        return table(self.__connection)

    def __commit(self) -> None:
        table_data = dict()
        for table_name, table in self.__tables.items():
            table_data[table_name] = {
                'fields': {name: datatype.__name__ for name, datatype in table.get_fields().items()}
            }
        with open(Database.__get_td_path(), 'w') as td:
            json.dump(table_data, td)

    def __update_table(self, table: Table) -> None:
        table_name = table.get_name()
        data = Database.__load_table_data(Database.__get_td_path())
        if data is not None and table_name in data:
            table_data = data[table_name]
            table = self.__tables[table_name]
            new_fields = table.get_fields()
            old_fields = table_data['fields']
            if (table_name in self.__tables) and (new_fields.keys() != old_fields.keys()):
                # t_class = type(self.__tables[table_name])
                # old_table = t_class(self.__connection, make_copy=True)
                old_table_values = table.select(*old_fields.keys(), as_dict=True).all()
                table.delete().table()
                table = self.__create_table(type(table))
                for row in old_table_values:
                    table.insert(**row)

    def table(self, name: str) -> Table:
        return self.__tables.get(name)

    def __init__(self, db_path: str = None, tables_path: str = None) -> None:
        if db_path is not None:
            self.__database_path = db_path
        if tables_path is not None:
            self.__tables_module = tables_path
        self.__connection = connect(self.__database_path)
        self.__cursor = self.__connection.cursor()
        tables = inspect.getmembers(sys.modules[self.__tables_module], inspect.isclass)
        for table_name, table in tables:
            if issubclass(table, Table) and table != Table:
                tb = self.__create_table(table)
                self.__tables[table_name] = tb
                self.__update_table(tb)
        self.__commit()
