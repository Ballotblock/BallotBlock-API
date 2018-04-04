#!/usr/bin/env python3
#
# src/account_types.py
# Authors:
#   Samuel Vargas
#

from typing import List
from enum import Enum, unique

@unique
class AccountType(Enum):
    voter = 1
    election_creator = 2

    @staticmethod
    def getEnumsAsList() -> List[str]:
        return [name for name in AccountType.__members__]

    @staticmethod
    def isValidType(name: str) -> bool:
        return name in AccountType.__members__
