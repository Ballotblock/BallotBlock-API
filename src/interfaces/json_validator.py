#!/usr/bin/env python3
#
# src/interfaces/json_validator.py
# Authors:
#     Samuel Vargas

from typing import Dict
import abc


class JsonValidator(abc.ABC):
    @abc.abstractmethod
    def is_valid(self, json_obj: Dict) -> (bool, str):
        raise NotImplementedError
