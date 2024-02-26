# package imports
import os
import sqlite3
import datetime

# local imports
import settings


class Sqlite:
    def __init__(self):
        db_path = os.path.join(settings.BASE_DIR, "sqlite.db")
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def migrate(self):
        """iterate through the list of services, and create
        table if DNE
        """
        _migrate_list = []
        for s in settings.SERVICES_LIST:
            # use `table` if exists or `name` as fallback
            _table_name = s.get("table") or s.get("name")

            # check if table exists
            _select = self.cur.execute(
                f"select name from sqlite_master where name like '{_table_name}'"
            )
            if not _select.fetchone():
                # create table if dne
                _query = f"create table if not exists {_table_name} ({settings.DB_SERVICES_TABLE_SCHEMA})"
                self.cur.execute(_query)

                # query the master table to check if table has been created successfully
                _select = self.cur.execute(
                    f"select name from sqlite_master where name like '{_table_name}'"
                )
                if len(_select.fetchone()) > 0:
                    _migrate_list.append(_table_name)

        if _migrate_list:
            print(f"migrations completed successfully for tables:\n{_migrate_list}")
        else:
            print(f"nothing to migrate...")

    def list_active_services(self, names=[]):
        _names = [s.name for s in settings.SERVICES_LIST]
        _unmatched = []
        _matched = []
        # match that the names are present in the list of services
        if names:
            for n in names:
                if n in _names:
                    _matched.append(n)
                else:
                    _unmatched.append(n)
        else:
            _matched = _names

        # if no matches (applicable only for named inputs)
        if not _matched:
            print(f"the input names did not match any services:\n{_unmatched}")
            return

        # query the db for the matches, and
        pass

    def get_latest(self, table_name):
        _query = f"select * from {table_name} order by id desc"
        _result = self.cur.execute(_query)
        return _result.fetchone()

    def save(self, table_name, pid, status="success"):
        _now = datetime.datetime.now()
        _data = [(None, pid, status, _now, _now)]
        self.cur.executemany(f"insert into {table_name} values (?, ?, ?, ?, ?)", _data)
        self.con.commit()

        # get the latest entry from db
        print(f"row added to table={table_name}")
        print(self.get_latest(table_name))
