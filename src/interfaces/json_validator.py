#!/usr/bin/env python3
#
# src/interfaces/json_validator.py
# Authors:
#     Samuel Vargas
import abc

class JsonValidator(abc.ABC):
    @abc.abstractmethod
    def is_valid(self) -> bool:
        pass

    @abc.abstractmethod
    def reason(self) -> str:
        pass