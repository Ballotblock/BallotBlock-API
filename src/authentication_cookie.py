# !/usr/bin/env python3
# src/intermediary.py
# Authors:
#     Samuel Vargas
#     Alex Gao

# https://github.com/pyca/cryptography/issues/1333#issuecomment-55481324
from src.cookie_encryptor import CookieEncryptor
from src.account_types import AccountType
from typing import Optional
from json import JSONDecodeError
import json

class AuthenticationCookie:
    @staticmethod
    def is_encrypted_by_registration_server(password: str, cookies) -> bool:
        try:
            token = json.loads(cookies.get("token"))
        except JSONDecodeError:
            return False

        for item in ('authentication', 'username', 'account_type'):
            if item not in token:
                return False

        if CookieEncryptor(password).decrypt(token['authentication'].encode('utf-8')) is None:
            return False

        return True

    @staticmethod
    def get_username(cookies) -> Optional[str]:
        try:
            token = json.loads(cookies.get("token"))
        except JSONDecodeError:
            return None

        return token.get('username')

    @staticmethod
    def get_account_type(cookies) -> Optional[AccountType]:
        try:
            token = json.loads(cookies.get("token"))
        except JSONDecodeError:
            return None

        if 'account_type' not in token:
            return None

        try:
            return AccountType(token['account_type'])
        except ValueError:
            return None