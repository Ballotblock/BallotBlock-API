#!/usr/bin/env python3
#
# src/interfaces/session_provider.py
# Authors:
#     Samuel Vargas

from flask import Session
import abc


class SessionProvider(abc.ABC):
    @abc.abstractmethod
    def authenticate_user(self, username: str, account_type: str, session: Session) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def unauthenticate_user(self, username: str, account_type: str, session: Session) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def is_authenticated(self, username: str, account_type: str, session: Session) -> bool:
        raise NotImplementedError
