#!/usr/bin/env python3
#
# src/cookie_encryptor.py
# Authors:
#     Samuel Vargas

# https://github.com/pyca/cryptography/issues/1333#issuecomment-55481324
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import os
import base64


class CookieEncryptor:
    def __init__(self, password: str):
        backend = default_backend()
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=backend
        )

        self.__key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        self.__fernet = Fernet(self.__key)

    def encrypt(self, data: bytes) -> bytes:
        return self.__fernet.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        return self.__fernet.decrypt(data)
