#!/usr/bin/env python3
#
# src/crypto_suite.py
# Authors:
#   Samuel Vargas
#

from typing import NamedTuple
from ecdsa import SigningKey, VerifyingKey
from cryptography.fernet import Fernet
import base64
import ecdsa
import rsa
import os

ECDSA_CURVE = ecdsa.SECP256k1


class FernetCrypt:
    def __init__(self, use_fernet_key_bytes: bytes = None):
        if use_fernet_key_bytes is not None:
            self.__key = use_fernet_key_bytes
        else:
            self.__key = Fernet.generate_key()
        self.__fernet = Fernet(self.__key)

    def get_key_as_bytes(self) -> bytes:
        return self.__key

    def get_key_as_b64(self) -> bytes:
        return base64.b64encode(self.__key)

    def encrypt_to_b64(self, data: bytes) -> bytes:
        return base64.b64encode(self.__fernet.encrypt(data))

    def decrypt_b64_to_bytes(self, ciphertext_b64: bytes) -> bytes:
        return self.__fernet.decrypt(base64.b64decode(ciphertext_b64))


class RSAKeyPair:
    def __init__(self, use_public_pkcs1_b64_key: bytes = None,
                 use_private_pkcs1_b64_key: bytes = None,
                 AES_KEY_SIZE=2048):
        if (bool(use_public_pkcs1_b64_key) and not bool(use_private_pkcs1_b64_key)) \
                or (not bool(use_public_pkcs1_b64_key) and bool(use_private_pkcs1_b64_key)):
            raise ValueError("Provide a RSA public private key string pair for both parameters.")

        if use_public_pkcs1_b64_key and use_private_pkcs1_b64_key:
            public_str = base64.b64decode(use_public_pkcs1_b64_key).decode('utf-8').strip(" \n\t\r")
            private_str = base64.b64decode(use_private_pkcs1_b64_key).decode('utf-8').strip(" \n\t\r")
            self.__public = rsa.PublicKey.load_pkcs1(public_str)
            self.__private = rsa.PrivateKey.load_pkcs1(private_str)
        else:
            self.__public, self.__private = rsa.newkeys(AES_KEY_SIZE)

    def get_public_key_as_pkcs1_b64(self) -> bytes:
        return base64.b64encode(self.__public.save_pkcs1())

    def get_private_key_as_pkcs1_b64(self):
        return base64.b64encode(self.__private.save_pkcs1())

    def encrypt_message_as_b64(self, data: bytes):
        return base64.b64encode(rsa.encrypt(data, self.__public))

    def decrypt_b64_to_bytes(self, ciphertext_b64: bytes) -> bytes:
        return rsa.decrypt(base64.b64decode(ciphertext_b64), self.__private)

class ECDSAKeyPair:
    def __init__(self, use_private_key_b64: bytes = None):
        if use_private_key_b64:
            self.__private = SigningKey.from_string(base64.b64decode(use_private_key_b64), curve=ECDSA_CURVE)
        else:
            self.__private = SigningKey.generate(curve=ECDSA_CURVE)
        self.__public = self.__private.get_verifying_key()

    def get_public_key(self) -> VerifyingKey:
        return self.__public

    def get_private_key(self) -> SigningKey:
        return self.__private

    def get_public_key_b64(self) -> bytes:
        return base64.b64encode(self.__public.to_string())

    def get_private_key_b64(self) -> bytes:
        return base64.b64encode(self.__private.to_string())

    def sign_with_private_key_and_retrieve_b64_signature(self, data: bytes) -> bytes:
        return base64.b64encode(self.__private.sign(data))

    def is_signed(self, signature_b64: bytes, data: bytes) -> bool:
        return self.__public.verify(base64.b64decode(signature_b64), data)
