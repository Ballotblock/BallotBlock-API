#!/usr/bin/env python3
#
# src/interfaces/memory_session_provider.py
# Authors:
#     Samuel Vargas

from flask import Session
from src.interfaces.session_provider import SessionProvider


class MemorySessionProvider(SessionProvider):
    def authenticate_user(self, username: str, account_type: str, session: Session) -> None:
        session[username] = account_type

    def unauthenticate_user(self, username: str, account_type: str, session: Session) -> None:
        if not self.is_authenticated(username, account_type, session):
            raise KeyError("Cannot remove user {0}, was never authenticated".format(username))
        session.pop(username, None)

    def is_authenticated(self, username: str, account_type: str, session: Session) -> bool:
        return username in session
