import datetime
from typing import Any

from dateutil.parser import (
    ParserError,
    parse,
)


def replace_hex_sequences(match):

    hex_sequence = match.group(0).replace("\\x", "")
    byte_value = bytes.fromhex(hex_sequence)
    try:
        clean_string = byte_value.decode("utf-8")
    except UnicodeDecodeError as e:
        clean_string = ""
    return clean_string


def parse_date(value: Any) -> datetime.date:
    if isinstance(value, str):
        try:
            return parse(value).date()
        except ParserError as ex:
            raise ValueError("Invalid date format")
    return value


def check_not_empty_str(value: str) -> str:
    if not value.strip():
        raise ValueError("Empty title string")
    return value
