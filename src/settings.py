import os

BASE_DIR = "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-1])

"""
key: value
------------
name: <name_of_service> (must be unique)
command: "some stupid command"
logfile: <dirpath_to_put_logs> | if not_provided/None, use `BASE_DIR/logs`
table: <table_name_in_db> | if not_provided/None, use `name` (must be unique)
category: <category_types> # so that each category gets special treament if needed
inactive: True/False
"""
SERVICES_LIST = [
    {
        "name": "specialcarrots",
        "table": "carrots",
        "command": "zrok share reserved carrots --headless",
        "category": "zrok",
    }
]

# this schema will be common across all tables for services
# this is to be used as is, and is in correct sqlite format
DB_SERVICES_TABLE_SCHEMA = """
id integer primary key,
pid integer,
status text,
created_at text,
updated_at text
"""
