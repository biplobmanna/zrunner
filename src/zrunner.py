# package imports
import os
import psutil
import sqlite3

# local imports
import settings

p = psutil.process_iter(
    [
        "name",
        "status",
        "cwd",
        "cmdline",
    ]
)
zrok_process_list = []

for _p in p:
    # print(_p.info['name'])
    # break
    if "zrok" in _p.info["name"]:
        zrok_process_list.append(_p.info)


for z in zrok_process_list:
    print(z)


class Sqlite:
    def __init__(self):
        db_path = os.path.join(settings.BASE_DIR, "sqlite.db")
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def create_table_if_dne(self):
        """iterate through the list of services, and create
        table if DNE
        """
        for s in settings.SERVICES_LIST:
            _table_name = s.get("table") or s.get("name")
            # create table if dne
            _query = f"create table if not exists {_table_name} ({settings.DB_SERVICES_TABLE_SCHEMA})"
            # query the master table to check if table has been created successfully
            result = self.cur.execute(f"select name from sqlite_master where name like '{_table_name}'")
            if len(result.fetchone()) > 0:
                print(f"select ({_table_name}) created successfully!")


s = Sqlite()
s.create_table_if_dne()
