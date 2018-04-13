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
