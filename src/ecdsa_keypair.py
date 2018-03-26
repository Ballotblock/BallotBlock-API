#!/usr/bin/env python3
#
# src/key.py
# Authors:
#   Samuel Vargas
#

from typing import NamedTuple
from ecdsa import SigningKey, VerifyingKey
from cryptography.fernet import Fernet
import ecdsa
import rsa
import os

ECDSA_CURVE = ecdsa.SECP256k1
AES_KEY_SIZE = 2048

class FernetCrypt:
    def __init__(self, use_key: str = None):
        if use_key is not None:
            self.__key = use_key.encode('utf-8')
        else:
            self.__key = Fernet.generate_key()
        self.__fernet = Fernet(self.__key)

    def get_key(self) -> str:
        return self.__key.decode('utf-8')

    def encrypt(self, plaintext: str) -> str:
        return self.__fernet.encrypt(plaintext.encode('utf-8')).decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        return self.__fernet.decrypt(ciphertext.encode('utf-8')).decode('utf-8')

class RSAKeyPair:
    def __init__(self, use_public_pkcs1_key: str = None, use_private_pkcs1_key: str = None):
        if use_public_pkcs1_key is None and use_private_pkcs1_key is not None \
           or use_public_pkcs1_key is not None and use_private_pkcs1_key is None:
           ValueError("Provide a RSA public private key string pair for both parameters.")

        if use_public_pkcs1_key is not None and not use_private_pkcs1_key is not None:
            self.__public = rsa.PublicKey.load_pkcs1(use_public_pkcs1_key.encode('utf-8'))
            self.__private = rsa.PrivateKey.load_pkcs1(use_private_pkcs1_key.encode('utf-8'))
        else:
            self.__public, self.__private = rsa.newkeys(AES_KEY_SIZE)

    def get_public_key_as_pkcs1(self):
        return self.__public.save_pkcs1()

    def get_private_key_as_pkcs1(self):
        return self.__private.save_pkcs1()

    def encrypt_message_with_public_key(self, plaintext: str):
        return rsa.encrypt(plaintext.encode('utf-8'), self.__public)

    def decrypt_message_with_private_key(self, crypttext: bytes) -> str:
        return rsa.decrypt(crypttext, self.__private).decode('utf-8')


class ECDSAKeyPair:
    def __init__(self, use_private_hex_key: str = None):
        if use_private_hex_key:
            self.__private = SigningKey.from_string(bytes.fromhex(use_private_hex_key))
        else:
            self.__private = SigningKey.generate(curve=ECDSA_CURVE)
        self.__public = self.__private.get_verifying_key()

    def get_public_key(self) -> VerifyingKey:
        return self.__public

    def get_private_key(self) -> SigningKey:
        return self.__private

    def get_public_key_hex_str(self) -> str:
        return str(self.__public.to_string().hex())

    def get_private_key_hex_str(self) -> str:
        return str(self.__private.to_string().hex())

    def sign_with_private_key_and_retrieve_hex_signature(self, plaintext: str) -> str:
        return str(self.__private.sign(plaintext.encode('utf-8')).hex())

    def is_signed_with_private_key(self, signature_hex: str, plaintext):
        return self.__public.verify(bytes.fromhex(signature_hex), bytes(plaintext.encode('utf-8')))

    @staticmethod
    def is_data_signed(public_key_hex: str, signature_hex: str, plaintext: str) -> bool:
        public_key_bytes = bytes.fromhex(public_key_hex)
        public_key = VerifyingKey.from_string(public_key_bytes, curve=ECDSA_CURVE)
        signature = bytes.fromhex(signature_hex)
        return public_key.verify(signature, bytes(plaintext.encode('utf-8')))