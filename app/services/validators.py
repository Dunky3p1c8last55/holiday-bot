import re
from datetime import datetime


def is_valid_city(value: str) -> bool:
    if not value:
        return False
    value = value.strip()
    return bool(re.fullmatch(r"[A-Za-zА-Яа-яЁё\s\-]{2,64}", value))


def is_valid_date(value: str, fmt: str = "%d.%m.%Y") -> bool:
    try:
        datetime.strptime(value or "", fmt)
        return True
    except ValueError:
        return False
