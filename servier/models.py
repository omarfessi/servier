from pydantic import BaseModel, BeforeValidator
from typing import Annotated
import datetime
import re

from .utils.models_helper import parse_date, check_not_empty_str, replace_hex_sequences
from .config import HEX_PATTERN

Date = Annotated[datetime.date, BeforeValidator(parse_date)]
NonEmptyStr = Annotated[str, BeforeValidator(check_not_empty_str)]
XFreeNonEmptyStr = Annotated[
    str,
    BeforeValidator(check_not_empty_str),
    BeforeValidator(lambda x: re.sub(HEX_PATTERN, replace_hex_sequences, x)),
]


class PubClinical(BaseModel):
    title: XFreeNonEmptyStr
    date: Date
    journal: XFreeNonEmptyStr
    source_file: str
    source_file_type: str

    class Config:
        extra = "ignore"


class Drug(BaseModel):
    atccode: NonEmptyStr
    drug: NonEmptyStr
    source_file: str = "drugs.csv"
    source_file_type: str = "csv"


class CrossReference(BaseModel):
    drug: NonEmptyStr
    journal: str
    mention_date: Date
    source_file: str
    ingestion_timestamp: datetime.datetime = datetime.datetime.now()
