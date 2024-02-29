# package imports
import psutil
import subprocess
import os
import signal
import logging

# local imports
import settings
import util
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
        # logger
        self.log = logging.getLogger("proc")
        self.log.setLevel(logging.INFO)
        # handler
        file_handler = logging.FileHandler(
            f"{settings.BASE_DIR}/logs/zrunner.log", mode="a"
        )
        file_handler.setLevel(logging.INFO)
        # formatter
        formatter = logging.Formatter(
            "[%(asctime)s :: %(name)s :: %(levelname)s] :: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        # combine all
        file_handler.setFormatter(formatter)
        self.log.addHandler(file_handler)

    def is_running(self, table_name: str) -> bool:
        self.log.info(f"is_running({table_name})")
        # getting the latest pid entry
        _row = self.db.get_latest(table_name)
        # check if any matching process with pid (idx=1 in row) is running
        if _row and _row[1] and psutil.pid_exists(_row[1]):
            return True
        else:
            return False

    def run(self, name: str) -> None:
        self.log.info(f"run({name})")
        # get meta data for the service name
        _data = util.get_services_data_by_name(name)

        # if no match, return
        if not _data:
            self.log.error(f"service {name} not found!")
            return

        # if the service is marked inactive
        if _data.get("inactive"):
            self.log.warning(f"service {name} is marked inactive...")
            return

        # query the db, get the latest pid, and check if that's running
        _table_name = _data.get("table") or _data.get("name")
        if self.is_running(_table_name):
            # since it's running, nothing to do, return
            self.log.info(f"service {name} is already up and running...")
            return

        # if nothing is running, let's run this shit
        _cmd = f"{_data['command']} > {settings.BASE_DIR}/logs/{name} 2>&1 &"
        self.log.info(f"service {name} is starting...")
        p = subprocess.Popen(_cmd, shell=True)

        # since we're running the command through a shell, the pid returned will be that of the shell
        # so, the pid + 1 (not 100% sure though, needs to be tested thoroughly) should be the command's pid
        _pid = p.pid + 1
        # find the pid using scanning list of all running services
        _pid2 = self.find_pid_using_service_command(_data["command"])
        # if both don't match, then it's a lol situation
        # this is definite proof that [pid = pid + 1] is non-deterministic
        if _pid != _pid2:
            self.log.warning(
                f"pid from subprocess don't match that of the actual process"
            )
            self.log.warning(f"[pid1={_pid}, pid2={_pid2}]")
            # use pid2 as this is the correct one
            _pid = _pid2

        # add entry to db
        self.db.save(_table_name, _pid)

    def run_all(self, names=[]):
        self.log.info(f"run_all({names})")
        _names = [s.get("name") for s in settings.SERVICES_LIST]
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
            self.log.error(f"the input names did not match any services:{_unmatched}")
            return

        for n in _matched:
            self.run(n)

    def find_pid_using_service_command(self, service_command):
        self.log.info(f"find_pid_using_service_command({service_command})")
        # run `ps ax` to get list of running processes
        _ps = subprocess.Popen(
            ["ps", "ax"], stdout=subprocess.PIPE, universal_newlines=True
        )
        # iterate through the list of running processes and find the one containing the service_command
        for line in _ps.stdout:
            if service_command in line:
                return line.split(" ")[0]

    def stop(self, name) -> None:
        self.log.info(f"stop({name})")
        _data = util.get_services_data_by_name(name)
        # if no match, return
        if not _data:
            self.log.error(f"service {name} not found!")
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
            self.log.info(f"service '{name}' stopped successfully!")
            return
        # stop the process with _pid using os and signal
        os.kill(_pid, signal.SIGTERM)

        # print stop service status
        self.log.info(f"service '{name}' stopped successfully!")

    def stop_all(self, names=[]):
        self.log.info(f"stop_all({names})")
        _names = [s.get("name") for s in settings.SERVICES_LIST]
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
            self.log.error(f"the input names did not match any services:{_unmatched}")
            return

        for n in _matched:
            self.stop(n)

    def list_all_services(self, names=[]):
        self.log.info(f"list_all_services({names})")
        _names = [s.get("name") for s in settings.SERVICES_LIST]
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
            self.log.error(f"the input names did not match any services:{_unmatched}")
            return

        print("\n============================================")
        print("Service Details:")
        print("============================================\n")
        # for each of the service names:
        # 1. find the latest entry in db
        # 2. find their current status if `inactive=false`
        # 3. display all details
        for _name in _matched:
            _data = util.get_services_data_by_name(_name)
            _table_name = _data.get("table") or _data.get("name")
            _latest = self.db.get_latest(_table_name)
            _pid = _latest[1]
            _cmd_list = ["ps", "-Flww", "-p", str(_pid)]
            _ps = subprocess.Popen(
                _cmd_list, stdout=subprocess.PIPE, universal_newlines=True
            )
            # print all the details below
            for k, v in _data.items():
                print(f"{k}: {v}")
            print("\nprocess status:")
            print("---------------")
            for line in _ps.stdout:
                print(line)
            print("--------------------------------------------\n")
