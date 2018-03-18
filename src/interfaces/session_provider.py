#!/usr/bin/env python3
#
# src/interfaces/session_provider.py
# Authors:
#     Samuel Vargas

import abc


class SessionProvider(abc.ABC):

    @abc.abstractmethod
    def authenticate_user(self, username: str)-> str:
        raise NotImplementedError

    @abc.abstractmethod
    def unauthenticate_user(self, username: str)-> None:
        raise NotImplementedError

    @abc.abstractmethod
    def is_authenticated(self, username: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_id(self) -> str:
        raise NotImplementedError
