# !/usr/bin/env python3
# src/intermediary.py
# Authors:
#     Samuel Vargas
#     Alex Gao

from src.httpcode import *
from src.cookie_encryptor import CookieEncryptor
from src.authentication_cookie import AuthenticationCookie
from src.account_types import AccountType
from test.config import test_backend
from test.test_util import JSON_HEADERS
from copy import deepcopy
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
        self.app.set_cookie("localhost", "token", json.dumps(self.auth_token))
        response = self.app.post("/api/authentication", headers=JSON_HEADERS)
        assert response.data.decode('utf-8') == VALID_AUTHENTICATION_COOKIE.message

    def test_authentication_that_isnt_encrypted_with_password_is_rejected(self):
        malformed = deepcopy(self.auth_token)
        malformed['authentication'] = ";-^)"
        self.app.set_cookie("localhost", "token", json.dumps(malformed))
        response = self.app.post("/api/authentication", headers=JSON_HEADERS)
        assert response.data.decode('utf-8') == MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE.message

    def test_missing_authentication_rejected(self):
        malformed = deepcopy(self.auth_token)
        malformed.pop('authentication')
        self.app.set_cookie("localhost", "token", json.dumps(malformed))
        response = self.app.post("/api/authentication", headers=JSON_HEADERS)
        assert response.data.decode('utf-8') == MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE.message

    def test_missing_username_rejected(self):
        malformed = deepcopy(self.auth_token)
        malformed.pop('username')
        self.app.set_cookie("localhost", "token", json.dumps(malformed))
        response = self.app.post("/api/authentication", headers=JSON_HEADERS)
        assert response.data.decode('utf-8') == MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE.message

    def test_missing_account_type(self):
        malformed = deepcopy(self.auth_token)
        malformed.pop('account_type')
        self.app.set_cookie("localhost", "token", json.dumps(malformed))
        response = self.app.post("/api/authentication", headers=JSON_HEADERS)
        assert response.data.decode('utf-8') == MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE.message

    def test_get_username(self):
        assert self.username == AuthenticationCookie.get_username({'token': json.dumps(self.auth_token)})

    def test_get_account_type(self):
        assert AccountType.election_creator == AuthenticationCookie.get_account_type({'token': json.dumps(self.auth_token)})
