#!/usr/bin/env python3
#
# src/cookie_encryptor.py
# Authors:
#     Samuel Vargas

# https://github.com/pyca/cryptography/issues/1333#issuecomment-55481324
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidSignature, InvalidToken
from typing import Optional
import base64


class CookieEncryptor:
    def __init__(self, password: str):
        backend = default_backend()
        # TODO: Constant salt is bad practice
        salt = b'\xb3?mT\x02\x839C\xc2V\x7f\xa7e\xc3\xa6m'
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

    def decrypt(self, data: bytes) -> Optional[bytes]:
        try:
            return self.__fernet.decrypt(data)
        except InvalidSignature:
            return None
        except InvalidToken:
            return None
