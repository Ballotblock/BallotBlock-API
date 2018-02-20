#!/usr/bin/env python3
#
# src/user.py
# Authors:
#     Samuel Vargas
#

import abc
from src import key

class User(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_elections(self):
        """
        An election consists of a list of propositions and
        a valid start / end range.
        """
        raise NotImplementedError("User() is an interface.")

    @abc.abstractmethod
    def get_ballots(self):
        """
        Ballots are lists of propositions tied to a particular
        election.
        """
        raise NotImplementedError("User() is an interface.")