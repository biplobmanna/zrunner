# package imports
import psutil
import subprocess
import os
import signal

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

    def get_services_data(self, name) -> dict[str:str]:
        _data = None
        for s in settings.SERVICES_LIST:
            if s["name"] == name:
                _data = s
                break
        return _data

    def run(self, name: str) -> None:
        # get meta data for the service name
        _data = self.get_services_data(name)

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
        # find the pid using scanning list of all running services
        _pid2 = self.find_pid_using_service_command(_data["command"])
        # if both don't match, then it's a lol situation
        # this is definite proof that [pid = pid + 1] is non-deterministic
        if _pid != _pid2:
            print(f"pid from subprocess don't match that of the actual process")
            print(f"[pid1={_pid}, pid2={_pid2}]")
            # use pid2 as this is the correct one
            _pid = _pid2

        # add entry to db
        self.db.save(_table_name, _pid)

    def find_pid_using_service_command(self, service_command):
        # run `ps ax` to get list of running processes
        _ps = subprocess.Popen(
            ["ps", "ax"], stdout=subprocess.PIPE, universal_newlines=True
        )
        # iterate through the list of running processes and find the one containing the service_command
        for line in _ps.stdout:
            if service_command in line:
                return line.split(" ")[0]

    def stop(self, name) -> None:
        _data = self.get_services_data(name)

        # if no match, return
        if not _data:
            print(f"service {name} not found!")
            return

        # irrespective of inactive, still check running task and stop
        _table_name = _data.get("table") or _data.get("name")

        # 1st pass: check exists, then stop
        if self.is_running(_table_name):
            _row = self.db.get_latest(_table_name)
            _pid = _row[1]
            _cmd = f"kill -15 {_pid}"
            p = subprocess.Popen(_cmd, shell=True)

        # 2nd pass: grep the logs path to get the service uniquely
        _pid = self.find_pid_using_service_command(_data["command"])
        # if nothing found, no harm, no foul
        if _pid is None:
            return
        # stop the process with _pid using os and signal
        os.kill(_pid, signal.SIGTERM)
