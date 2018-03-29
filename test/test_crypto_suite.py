#!/usr/bin/env python3
#
# test/test_crypto_suite.py
# Authors:
#   Samuel Vargas
#

import unittest
import base64
import json
from ecdsa import SigningKey,VerifyingKey
from src.crypto_suite import ECDSAKeyPair, RSAKeyPair, FernetCrypt, ECDSA_CURVE
from src.crypto_flow import verify_data_is_signed_ecdsa

# These keys are unimportant and are only used for verifying that
# b64 conversion / serialization works correctly. Do not use them for
# anything important!

DUMMY_RSA_PRIVATE_KEY = base64.b64encode("""
-----BEGIN RSA PRIVATE KEY-----
MIIBPQIBAAJBAJwII+9oFrq/VvkVDSTO3DjJ40/ga10kCJMRxP9V+pSDusSgylq7
zTbiFz2ORrsGUyTEQC8riYVycPW0kF+xpaECAwEAAQJAV62vW8mW9CuvGNq+fw+K
6pJwHKOUUUt9Uf9rPrw2TJ61V6LouRuaVPfNW5vh6fC9nePD6OWY9I7Q/j4Xq5t8
7QIjAN9RmmWqlye3ieyMrkrjkeEIOje/LdicMyQ9mWNiKB6QI2cCHwCy3bQhTYad
jK6sXTyvLlMs3Os2aK6FjuMYyZqtkbcCInR1eOAl+1fSBlJe9xHE5bGF+d5Si9UX
eDAhE5nZeXSe1GcCHwCyWab3XhpQlqrFa+LKuuJs5YwUIKWEv0lqufvl/lkCIwDG
ZXS3llhT1ZVi7HWiubyS2VAsPhCAr/+ZHkzrYxkqRTep
-----END RSA PRIVATE KEY-----
""".encode('utf-8'))

DUMMY_RSA_PUBLIC_KEY = base64.b64encode("""
-----BEGIN RSA PUBLIC KEY-----
MEgCQQCcCCPvaBa6v1b5FQ0kztw4yeNP4GtdJAiTEcT/VfqUg7rEoMpau8024hc9
jka7BlMkxEAvK4mFcnD1tJBfsaWhAgMBAAE=
-----END RSA PUBLIC KEY-----
""".encode('utf-8'))


class FernetCryptTest(unittest.TestCase):
    def test_verify_fernet_b64_conversion(self):
        fernet = FernetCrypt()
        assert type(fernet.get_key_as_b64()) == bytes
        original_message = "This is a message we're encrypting.".encode('utf-8')
        cipher_b64 = fernet.encrypt_to_b64(original_message)
        assert type(cipher_b64) == bytes
        decrypted_message = fernet.decrypt_b64_to_bytes(cipher_b64)
        assert decrypted_message == original_message

    def test_fernet_key_serialization(self):
        fernet_key = FernetCrypt()
        fernet_key_serialized = FernetCrypt(fernet_key.get_key_as_bytes())

        # Verify that the keys are the same
        assert fernet_key.get_key_as_b64() == fernet_key_serialized.get_key_as_b64()

        # Verify that we can encrypt / decrypt
        original_message = "This is the original message.".encode('utf-8')
        a = fernet_key.decrypt_b64_to_bytes(fernet_key.encrypt_to_b64(original_message))
        b = fernet_key_serialized.decrypt_b64_to_bytes(fernet_key_serialized.encrypt_to_b64(original_message))
        assert a == b


class RSAKeyPairTest(unittest.TestCase):
    def test_verify_rsa_b64_conversion(self):
        original_message = "This is the original message.".encode('utf-8')
        rsa_key = RSAKeyPair(use_private_pkcs1_b64_key=DUMMY_RSA_PRIVATE_KEY,
                             use_public_pkcs1_b64_key=DUMMY_RSA_PUBLIC_KEY)
        ciphertext_b64 = rsa_key.encrypt_message_as_b64(original_message)
        assert type(ciphertext_b64) == bytes
        assert original_message == rsa_key.decrypt_b64_to_bytes(ciphertext_b64)

    def test_rsa_key_serialization(self):
        original_message = "This is the original message.".encode('utf-8')
        rsa_key = RSAKeyPair(use_private_pkcs1_b64_key=DUMMY_RSA_PRIVATE_KEY,
                             use_public_pkcs1_b64_key=DUMMY_RSA_PUBLIC_KEY)
        rsa_key_clone = RSAKeyPair(use_private_pkcs1_b64_key=rsa_key.get_private_key_as_pkcs1_b64(),
                                   use_public_pkcs1_b64_key=rsa_key.get_public_key_as_pkcs1_b64())

        # Keys should be identical if one is created from serialized file
        assert rsa_key.get_private_key_as_pkcs1_b64() == rsa_key_clone.get_private_key_as_pkcs1_b64()
        assert rsa_key.get_public_key_as_pkcs1_b64() == rsa_key_clone.get_public_key_as_pkcs1_b64()

        # Swapping keys should work fine
        a = rsa_key_clone.decrypt_b64_to_bytes(rsa_key.encrypt_message_as_b64(original_message))
        b = rsa_key.decrypt_b64_to_bytes(rsa_key_clone.encrypt_message_as_b64(original_message))
        assert a == b

    def test_cant_create_rsa_key_with_just_public_or_private_key(self):
        def wrapper(**kwargs):
            RSAKeyPair(**kwargs)

        self.assertRaises(ValueError, wrapper, use_private_pkcs1_b64_key=b"Don't care")
        self.assertRaises(ValueError, wrapper, use_public_pkcs1_b64_key=b"Don't care")

class ECDSAKeyPairTest(unittest.TestCase):
    def test_ecdsa_b64_conversion(self):
        original_message = "This is the original message.".encode('utf-8')
        ecdsa_key = ECDSAKeyPair()
        signature_b64 = ecdsa_key.sign_with_private_key_and_retrieve_b64_signature(original_message)
        assert ecdsa_key.is_signed(signature_b64, original_message)

    def test_ecdsa_serialization(self):
        original_message = "This is the original message.".encode('utf-8')
        ecdsa_key = ECDSAKeyPair()
        ecdsa_key_clone = ECDSAKeyPair(use_private_key_b64=ecdsa_key.get_private_key_b64())

        assert ecdsa_key.get_private_key_b64() == ecdsa_key_clone.get_private_key_b64()
        assert ecdsa_key.get_public_key_b64() == ecdsa_key_clone.get_public_key_b64()

    def test_ecdsa_signing(self):
        ecdsa_key = ECDSAKeyPair()
        data = json.dumps({ "Don't" : "Care" })
        signature = ecdsa_key.sign_with_private_key_and_retrieve_b64_signature(data.encode('utf-8'))
        public_key = base64.b64decode(ecdsa_key.get_public_key_b64())

        # Create a VerifyingKey from a ECDSAKeyPair, we can use this key
        vk = VerifyingKey.from_string(base64.b64decode(ecdsa_key.get_public_key_b64()), curve=ECDSA_CURVE)
        assert vk.verify(base64.b64decode(signature), data.encode('utf-8'))

