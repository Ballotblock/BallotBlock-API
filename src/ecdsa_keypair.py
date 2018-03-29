#!/usr/bin/env python3
#
# src/key.py
# Authors:
#   Samuel Vargas
#

from typing import NamedTuple
import ecdsa
from ecdsa import SigningKey, VerifyingKey

ECDSA_CURVE = ecdsa.SECP256k1
ECDSA_256k1_KeyPair = NamedTuple("ECDSA_256k1_KeyPair", [("public", VerifyingKey), ("private", SigningKey)])


class ECDSAKeyPair:
    def __init__(self):
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