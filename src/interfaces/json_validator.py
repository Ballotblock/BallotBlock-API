#!/usr/bin/env python3
#
# src/interfaces/json_validator.py
# Authors:
#     Samuel Vargas

from typing import Dict
from typing import NamedTuple
from collections import namedtuple
import abc

JsonValidity = namedtuple("jsonvalidty", ("reason", "valid"))


class JsonValidator(abc.ABC):
    @abc.abstractmethod
    def is_valid(self, json_obj: Dict) -> JsonValidity:
        pass
