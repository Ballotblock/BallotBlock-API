#!/usr/bin/env python3
#
# test/test_crypto_suite.py
# Authors:
#   Samuel Vargas
#

import unittest
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from src.crypto_suite import CryptoSuite, ECDSA_256k1_KeyPair


class Person:
    def __init__(self, message: bytes, keys: ECDSA_256k1_KeyPair):
        self.__message = message
        self.__keys = keys

    def get_message(self):
        return self.__message

    def get_public_key(self) -> VerifyingKey:
        return self.__keys.public

    def get_private_key(self) -> SigningKey:
        return self.__keys.private


class KeyTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.alice = Person(b"All your base are belong to us", CryptoSuite.generate_key_pair())
        self.bob = Person(b"Somebody set us up the bomb", CryptoSuite.generate_key_pair())

    def test_alice_verify_message(self):
        message = self.alice.get_message()
        signed_message = self.alice.get_private_key().sign(message)
        assert self.alice.get_public_key().verify(signed_message, message), \
            "Alice can sign a message and verify she was the one who signed it."

    def test_bob_cannot_verify_alices_message(self):
        message = self.alice.get_message()
        alice_signed_message = self.alice.get_private_key().sign(message)
        with self.assertRaises(BadSignatureError) as cm:
            cm.expected.__name__ = "Bob should not be able to verify Alice's signed message" \
                                   "using his own public key."

            self.bob.get_public_key().verify(alice_signed_message, message)
