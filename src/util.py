# local imports
import settings


def get_services_data_by_name(name) -> dict[str:str] | None:
    for s in settings.SERVICES_LIST:
        if s["name"] == name:
            return s


def get_table_by_name(name: str) -> str | None:
    for s in settings.SERVICES_LIST:
        if s["name"] == name:
            return s.get("table") or s.get("name")
