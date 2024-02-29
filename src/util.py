# package imports
import logging

# local imports
import settings

# logger
log = logging.getLogger("util")
log.setLevel(logging.INFO)
# handler
file_handler = logging.FileHandler(f"{settings.BASE_DIR}/logs/zrunner.log", mode="a")
file_handler.setLevel(logging.INFO)
# formatter
formatter = logging.Formatter(
    "[%(asctime)s :: %(name)s :: %(levelname)s] :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# combine all
file_handler.setFormatter(formatter)
log.addHandler(file_handler)


def get_services_data_by_name(name) -> dict[str:str] | None:
    log.info(f"get_services_data_by_name({name})")
    for s in settings.SERVICES_LIST:
        if s["name"] == name:
            return s


def get_table_by_name(name: str) -> str | None:
    log.info(f"get_table_by_name({name})")
    for s in settings.SERVICES_LIST:
        if s["name"] == name:
            return s.get("table") or s.get("name")
