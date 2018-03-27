#!/usr/bin/env python3
#
# src/crypto_flow.py
# Authors:
#   Samuel Vargas
#

import base64
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from src.crypto_suite import ECDSAKeyPair


def verify_data_is_signed_ecdsa(
        data: bytes = None,
        string_signature_b64: bytes = None,
        user_public_key_ecdsa_b64: bytes = None) -> bool:
    public_key = VerifyingKey().from_string(base64.b64decode(user_public_key_ecdsa_b64))
    try:
        result = public_key.verify(base64.b64decode(string_signature_b64), data)
    except BadSignatureError:
        return False

    return True
