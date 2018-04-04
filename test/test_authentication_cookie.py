# !/usr/bin/env python3
# src/intermediary.py
# Authors:
#     Samuel Vargas
#     Alex Gao

from src.cookie_encryptor import CookieEncryptor
from src.authentication_cookie import AuthenticationCookie
from src.account_types import AccountType
import unittest
import uuid

class AuthenticationCookieTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        password = "hunter2"
        random = '6862cff6-d5f7-440a-a02e-573c4be9f944'.encode('utf-8')
        self.cookie_encryptor = CookieEncryptor(password)
        self.token = {
            "username": "User",
            "account_type": AccountType.voter,
            "expires": "never",
            "authentication": self.cookie_encryptor.encrypt(random).decode('utf-8')
        }