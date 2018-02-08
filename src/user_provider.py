#!/usr/bin/env python3
#
# src/user_provider.py
# Authors:
#     Samuel Vargas
#

import abc
from src import key

class UserProvider(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_user(self):
        pass