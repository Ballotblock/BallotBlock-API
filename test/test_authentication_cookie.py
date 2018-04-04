# !/usr/bin/env python3
# src/intermediary.py
# Authors:
#     Samuel Vargas
#     Alex Gao

from src.cookie_encryptor import CookieEncryptor
from src.authentication_cookie import AuthenticationCookie
from src.account_types import AccountType
from test.config import test_backend
import json
import unittest
import src.intermediary


class AuthenticationCookieTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # Setup an election
        self.username = "Alice"
        self.password = "hunter2"
        self.app = src.intermediary.start_test(test_backend(), self.password)

        # Setup Authentication Cookie
        self.auth_token = {
            'username': self.username,
            'account_type': AccountType.election_creator.value,
            'authentication': CookieEncryptor(self.password).encrypt(b"ABC").decode('utf-8')
        }


    def test_is_encrypted_by_registration_server(self):
        assert AuthenticationCookie.is_encrypted_by_registration_server(self.password, {'token': json.dumps(self.auth_token)})

    def test_get_username(self):
        assert self.username == AuthenticationCookie.get_username({'token': json.dumps(self.auth_token)})

    def test_get_account_type(self):
        assert AccountType.election_creator == AuthenticationCookie.get_account_type({'token': json.dumps(self.auth_token)})
