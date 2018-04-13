# !/usr/bin/env python3
#
# src/mock_server.py
# Authors:
#     Samuel Vargas
#
# Simple mock server for rapid testing / application demoing purposes.
#

import unittest
from unittest.mock import MagicMock
from src.account_types import AccountType
from src.intermediary import app
from src.authentication_cookie import AuthenticationCookie
from src.sqlite import SQLiteBackendIO
import src.intermediary

USERNAME = "MockUser"
ACCOUNT_TYPE = AccountType.election_creator

AuthenticationCookie.get_username = MagicMock(return_value=USERNAME)
AuthenticationCookie.get_account_type = MagicMock(return_value=USERNAME)
AuthenticationCookie.is_encrypted_by_registration_server = MagicMock(return_value=True)


if __name__ == '__main__':
    src.intermediary.start(
        SQLiteBackendIO(":memory:"),
        url="127.0.0.1",
        port=8080
    )
