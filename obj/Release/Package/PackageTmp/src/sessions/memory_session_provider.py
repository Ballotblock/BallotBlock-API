#!/usr/bin/env python3
#
# src/interfaces/memory_session_provider.py
# Authors:
#     Samuel Vargas

from src.interfaces.session_provider import SessionProvider
from uuid import uuid4

class MemorySessionProvider(SessionProvider):

    def __init__(self):
        self.authenticated = {}

    def authenticate_user(self, username: str) -> str:
        id = uuid4()
        self.authenticated[username] = id
        return id

    def unauthenticate_user(self, username: str) -> None:
        if not self.is_authenticated(username):
            raise KeyError("Cannot remove user {0}, was never authenticated".format(username))
        self.authenticated.pop(username)

    def is_authenticated(self, username: str) -> bool:
        return username in self.authenticated

    def get_id(self) -> str:
        pass