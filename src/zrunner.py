# package imports
import argparse

# local imports
from db import Sqlite
from proc import Proc

# setup the arparser
description = """small lightweight python utility to check for running service,
and start them back up if they're not running.
"""
parser = argparse.ArgumentParser(description=description)

# arguments
# list all services, their settings, and running status...
parser.add_argument(
    "-l",
    "--list",
    nargs="*",
    help="list all the services being managed by zrunner, their current settings, and running status",
)

parser.add_argument(
    "--migrate",
    action=argparse.BooleanOptionalAction,
    help="migrate all the new services added if any",
)

parser.add_argument(
    "--run",
    nargs="*",
    help="run named services, or all services if no arguments provided",
)

parser.add_argument(
    "--stop",
    nargs="*",
    help="stop named services, or all services if no arguments provided",
)


# parse
args = parser.parse_args()

# execute by precedence
if args.list is not None:
    p = Proc()
    p.list_all_services(args.list)
    # nothing else is parsed, exit automatically
    exit(0)

if args.migrate:
    db = Sqlite()
    db.migrate()
    # nothing else is parsed, exit automatically
    exit(0)

if args.stop is not None:
    p = Proc()
    p.stop_all(args.stop)
    # nothing else is parsed, exit automatically
    exit(0)

if args.run is not None:
    p = Proc()
    p.run_all(args.run)
    # nothing else is parsed, exit automatically
    exit(0)
