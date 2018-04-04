#!/usr/bin/env python3
#
# tests/test_cookie_encryptor.py
# Authors:
#   Samuel Vargas
#

from src.account_types import AccountType
from src.server import app
from src.cookie_encryptor import CookieEncryptor
import unittest
import json


class CookieEncryptorTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.secret_password = "SECRET_PASSWORD"
        self.cookie_encryptor = CookieEncryptor(self.secret_password)

        # Create an account token
        self.token = {
            "username": "Sparky",
            "password": "Student Loans",
            "account_type": AccountType.voter.value
        }

    def test_can_encrypt_decrypt_cookie(self):
        # Encrypt the token
        uuid = '6862cff6-d5f7-440a-a02e-573c4be9f944'
        self.token['authentication'] = self.cookie_encryptor.encrypt(uuid.encode('utf-8')).decode('utf-8')
        assert self.token['authentication'] != uuid

        # Decrypt the token
        decrypted = self.cookie_encryptor.decrypt(self.token['authentication'].encode('utf-8'))
        assert uuid == decrypted.decode('utf-8')
