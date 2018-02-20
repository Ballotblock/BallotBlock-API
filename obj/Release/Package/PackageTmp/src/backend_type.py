#!/usr/bin/env python3
#
# src/backend_type.py
# Authors:
#     Samuel Vargas
#

from typing import List
from enum import Enum, unique


@unique
class BackendType(Enum):
    SQLite = 1
    HyperLedger = 2

    @staticmethod
    def get_enums_as_list() -> List[str]:
        return [name for name in BackendType.__members__]

    @staticmethod
    def is_valid_type(name: str) -> bool:
        return name in BackendType.__members__
