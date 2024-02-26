# package imports
import psutil
import subprocess

# local imports
import settings
from db import Sqlite

OPTIONS = [
    "name",
    "status",
    "cwd",
    "cmdline",
]


class Proc:
    def __init__(self):
        self.db = Sqlite()

    def is_running(self, table_name: str) -> bool:
        # getting the latest pid entry
        _row = self.db.get_latest(table_name)
        # check if any matching process with pid (idx=1 in row) is running
        if _row and psutil.pid_exists(_row[1]):
            return True
        else:
            return False

    def run(self, name: str) -> None:
        # get meta for the service name
        _data = None
        for s in settings.SERVICES_LIST:
            if s["name"] == name:
                _data = s
                break
        # if no match, return
        if not _data:
            print(f"service {name} not found!")
            return

        # if the service is marked inactive
        if _data.get("inactive"):
            print(f"service {name} is marked inactive...")
            return

        # query the db, get the latest pid, and check if that's running
        _table_name = _data.get("table") or _data.get("name")
        if self.is_running(_table_name):
            # since it's running, nothing to do, return
            print(f"service {name} is already up and running...")
            return

        # if nothing is running, let's run this shit
        _cmd = f"{_data['command']} > {settings.BASE_DIR}/logs/{name} 2>&1 &"
        p = subprocess.Popen(_cmd, shell=True)

        # since we're running the command through a shell, the pid returned will be that of the shell
        # so, the pid + 1 (not 100% sure though, needs to be tested thoroughly) should be the command's pid
        _pid = p.pid + 1

        # add entry to db
        self.db.save(_table_name, _pid)
