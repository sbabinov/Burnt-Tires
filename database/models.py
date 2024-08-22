from __future__ import annotations

import copy
from typing import Any, List, Tuple, Literal, Dict
from sqlite3 import Connection


class Datatype:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def convert_to_db(self):
        raise NotImplementedError

class ID(Datatype, int):
    def __new__(cls, *args, auto_update: bool = True, **kwargs):
        number = args[0] if args else 1
        return super(ID, cls).__new__(cls, number)

    def __init__(self, auto_update: bool = True) -> None:
        int.__init__(self)
        self.auto_update = auto_update

    def convert_to_db(self):
        return self

class INT(int, Datatype):
    def convert_to_db(self):
        return self

class BIGINT(int, Datatype):
    def convert_to_db(self):
        return self

class REAL(float, Datatype):
    def convert_to_db(self):
        return self

class TEXT(str, Datatype):
    def convert_to_db(self):
        return self

class LIST(list, Datatype):
    __separate = '; '

    def set_separate(self, separate: str) -> None:
        self.__separate = separate

    def convert_to_db(self):
        return str(self)

    def to_int(self):
        return [int(el) for el in self]

    def to_float(self):
        return [int(el) for el in self]

    def __init__(self, collection: list | tuple | str = None, separate: str = None) -> None:
        if separate is None:
            separate = LIST.__separate
        self.__separate = separate
        if collection is None:
            collection = []
        if isinstance(collection, str):
            collection = collection.split(self.__separate)
        list.__init__(self, copy.deepcopy(collection))

    def __str__(self) -> str:
        str_list = []
        for el in self:
            str_list.append(str(el))
        return self.__separate.join(str_list)


SQL_TYPES = {
    ID: 'INT',
    INT: 'INT',
    BIGINT: 'BIGINT',
    REAL: 'REAL',
    TEXT: 'TEXT',
    LIST: 'TEXT'
}

STR_TYPES = {
    'ID': INT,
    'INT': INT,
    'BIGINT': BIGINT,
    'REAL': REAL,
    'TEXT': TEXT,
    'LIST': LIST
}


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Selection:
    def __reset_row_factory(self) -> None:
        self.__connection.row_factory = None

    def __init__(self, connection: Connection, table_name: str, fields: dict,
                 purpose: Literal['SELECT', 'GET', 'UPDATE', 'DELETE'], *args, **kwargs) -> None:
        self.__connection = connection
        if kwargs.get('as_dict', False):
            self.__connection.row_factory = dict_factory
            del kwargs['as_dict']
        self.__cursor = self.__connection.cursor()
        self.__table_name = table_name
        self.__fields = fields
        self.__purpose = purpose
        self.__args = args
        if not self.__args:
            self.__args = tuple([name for name in fields])
        self.__kwargs = kwargs

        def get_str_args(a: tuple) -> str:
            str_a = ''
            for f in a:
                str_a += f'{f}, '
            return str_a[:-2]

        if self.__purpose in ('SELECT', 'GET'):
            str_args = get_str_args(self.__args)
            self.__base_query = f"SELECT {str_args} FROM '{self.__table_name}'"

        if self.__purpose == 'UPDATE':
            str_args = get_str_args(tuple(kwargs.keys()))
            self.__base_query = f"UPDATE '{self.__table_name}' SET ({str_args}) = ({('?, ' * len(kwargs))[:-2]})"

        if self.__purpose == 'DELETE':
            self.__base_query = f"DELETE FROM '{self.__table_name}'"

    def all(self) -> List[Any]:
        data = self.__cursor.execute(self.__base_query).fetchall()
        self.__reset_row_factory()
        return data

    def where(self, ne: dict = None, gt: dict = None, lt: dict = None, order_by: str = None,
              reverse_order: bool = False, **kwargs) -> List[Any] | Any:
        """ Finds entries in the table by specified criteria. """
        query = ' WHERE'
        query_args = []
        if self.__purpose == 'UPDATE':
            query_args += self.__kwargs.values()

        def paste_to_template(template: str, value: Any) -> str:
            q_part = ''
            for s in template:
                if s == '@':
                    q_part += value
                else:
                    q_part += s
            return q_part

        def update_query(q: str, q_template: str, q_args: list, d: dict) -> Tuple[str, List]:
            q_args = q_args.copy()
            for k, vs in d.items():
                if isinstance(vs, (list, tuple)) and not isinstance(vs, str):
                    for v in vs:
                        q += paste_to_template(q_template, k)
                        q_args.append(v)
                else:
                    q += paste_to_template(q_template, k)
                    q_args.append(vs)
            return q, q_args

        if kwargs:
            query, query_args = update_query(query, ' @ = ? AND', query_args, kwargs)
            query = query[:-3]
        if ne is not None:
            query, query_args = update_query(query, ' NOT @ = ? AND', query_args, ne)
            query = query[:-4]
        if gt is not None:
            query, query_args = update_query(query, ' @ > ? AND', query_args, gt)
            query = query[:-4]
        if lt is not None:
            query, query_args = update_query(query, ' @ < ? AND', query_args, lt)
            query = query[:-4]

        query = self.__base_query + query
        if self.__purpose in ('SELECT', 'GET'):
            if order_by:
                query += f' ORDER BY {order_by}'
            if reverse_order:
                query += ' DESC'

            data = self.__cursor.execute(query, tuple(query_args)).fetchall()
            processed_data = []
            if self.__connection.row_factory is None:
                for i in range(len(data)):
                    processed_data.append([])
                    for j in range(len(data[i])):
                        datatype = self.__fields[self.__args[j]]
                        processed_data[-1].append(datatype(data[i][j]))
            else:
                processed_data = data
            #     for i in range(len(data)):
            #         processed_data.append([])
            #         for j in data[i]:
            #             datatype = self.__fields[j]
            #             processed_data[-1].append(datatype(data[i][j]))
            if self.__purpose == 'GET':
                if processed_data:
                    if len(processed_data[0]) == 1:
                        processed_data = processed_data[0][0]
                    else:
                        processed_data = processed_data[0]
                else:
                    processed_data = None
            self.__reset_row_factory()
            return processed_data
        self.__reset_row_factory()
        self.__cursor.execute(query, tuple(query_args))
        self.__connection.commit()

    def table(self) -> None:
        if self.__purpose == 'DELETE':
            query = f"DROP TABLE '{self.__table_name}'"
            self.__cursor.execute(query)
            self.__connection.commit()

    def __del__(self) -> None:
        self.__reset_row_factory()


class Table:
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @staticmethod
    def is_correct_datatype(datatype: Any) -> bool:
        return datatype in SQL_TYPES

    def __get_last_id(self):
        data = self.__cursor.execute(f"SELECT id FROM '{self.__name}'").fetchall()
        if data:
            last_id = data[-1][0]
        else:
            last_id = 0
        return last_id

    def get_fields(self) -> Dict[str, Any]:
        fields = self.__dir__()
        field_data = []
        for field in fields:
            datatype = type(getattr(self, field))
            if Table.is_correct_datatype(datatype):
                field_data.append((field, datatype))
        return {key: value for key, value in field_data}

    def pickle(self) -> Table:
        table = Table(self.__connection)
        table.__connection = None
        return table

    def __init__(self, connection: Connection, make_copy: bool = False) -> None:
        self.__name = self.get_name()
        self.__connection = connection
        self.__cursor = self.__connection.cursor()
        if not hasattr(self, 'id'):
            self.id = ID()
        if not make_copy:
            fields_data = 'id INT PRIMARY KEY, '
            for field_name, field_datatype in self.get_fields().items():
                if field_name != 'id':
                    fields_data += f"'{field_name}' {SQL_TYPES[field_datatype]}, "
            fields_data = fields_data[:-2]
            self.__cursor.execute(f"CREATE TABLE IF NOT EXISTS '{self.__name}' ({fields_data})")
            self.__connection.commit()

    def insert(self, *args, **kwargs) -> None:
        table_fields = self.get_fields()
        entry_data = []
        if self.id.auto_update:
            entry_data.append(self.__get_last_id() + 1)
        ind = 0
        for field in table_fields.keys():
            if field != 'id' or not self.id.auto_update:
                datatype = self.get_fields()[field]
                if kwargs.get(field) is None:
                    try:
                        entry_data.append(datatype(args[ind]).convert_to_db())
                    except TypeError:
                        entry_data.append(None)
                    except IndexError:
                        entry_data.append(None)
                elif kwargs.get(field) != 'id':
                    entry_data.append(datatype(kwargs.get(field)).convert_to_db())
                ind += 1

        self.__cursor.execute(f"INSERT INTO '{self.__name}' VALUES "
                              f"({('?, ' * len(table_fields))[:-2]})", entry_data)
        self.__connection.commit()

    def update(self, **kwargs):
        return Selection(self.__connection, self.__name, self.get_fields(), 'UPDATE', **kwargs)

    def select(self, *args, as_dict: bool = False) -> Selection:
        return Selection(self.__connection, self.__name, self.get_fields(), 'SELECT', *args, as_dict=as_dict)

    def get(self, *args) -> Selection:
        return Selection(self.__connection, self.__name, self.get_fields(), 'GET', *args)

    def delete(self) -> Selection:
        return Selection(self.__connection, self.__name, self.get_fields(), 'DELETE', ())
