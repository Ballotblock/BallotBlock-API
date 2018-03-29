#!/usr/bin/env python3
#
# src/crypto_flow.py
# Authors:
#   Samuel Vargas
#

import base64
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from typing import Dict
from src.crypto_suite import ECDSAKeyPair, RSAKeyPair, FernetCrypt, ECDSA_CURVE




class CryptoFlow:
    @staticmethod
    def generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict() -> Dict:
        rsa = RSAKeyPair()
        fernet = FernetCrypt()
        encrypted_fernet_key = rsa.encrypt_message_as_b64(fernet.get_key_as_bytes())

        return {
            "election_public_key": rsa.get_public_key_as_pkcs1_b64().decode('utf-8'),
            "election_private_key": rsa.get_private_key_as_pkcs1_b64().decode('utf-8'),
            "election_encrypted_fernet_key": encrypted_fernet_key.decode('utf-8'),
        }

    @staticmethod
    def encrypt_vote_with_election_creator_rsa_keys_and_encrypted_fernet_key(
            ballot_str: str = None,
            rsa_public_key_b64: str = None,
            rsa_private_key_b64: str = None,
            encrypted_fernet_key: str = None):
        election_rsa = RSAKeyPair(
            use_public_pkcs1_b64_key=rsa_public_key_b64,
            use_private_pkcs1_b64_key=rsa_private_key_b64
        )

        # Decrypt the fernet symmetric key
        decrypted_fernet_key = election_rsa.decrypt_b64_to_bytes(encrypted_fernet_key.encode('utf-8'))
        fernet_crypt = FernetCrypt(use_fernet_key_bytes=decrypted_fernet_key)
        return fernet_crypt.encrypt_to_b64(ballot_str.encode('utf-8')).decode('utf-8')

    @staticmethod
    def verify_data_is_signed_ecdsa(
            data: bytes = None,
            string_signature_b64: bytes = None,
            user_public_key_ecdsa_b64: bytes = None) -> bool:
        public_key = VerifyingKey.from_string(base64.b64decode(user_public_key_ecdsa_b64), curve=ECDSA_CURVE)
        try:
            public_key.verify(base64.b64decode(string_signature_b64), data.encode('utf-8'))
        except BadSignatureError:
            return False

        return True
