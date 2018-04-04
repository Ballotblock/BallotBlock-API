# !/usr/bin/env python3
# src/intermediary.py
# Authors:
#     Samuel Vargas
#     Alex Gao

# https://github.com/pyca/cryptography/issues/1333#issuecomment-55481324
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken
from src.account_types import AccountType
from flask import request
import json
import os
import base64

class AuthenticationCookie:
    @staticmethod
    def is_encrypted_by_registration_server(cookies) -> bool:

    @staticmethod
    def get_username(cookies) -> str:
        token = json.loads(cookies.get("token"))
        return token['username']

    @staticmethod
    def get_account_type(cookies) -> str
        token = json.loads(cookies.get("token"))
        return token['account_type']
        return AccountType(token['account_type'])