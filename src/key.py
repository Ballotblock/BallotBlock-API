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
ECDSA_256k1_KeyPair = NamedTuple("hexkeypair", [("public", VerifyingKey), ("private", SigningKey)])


def generate_edsca_keypair() -> ECDSA_256k1_KeyPair:
    private = SigningKey.generate(curve=ECDSA_CURVE)
    public = private.get_verifying_key()
    return ECDSA_256k1_KeyPair(public, private)


def hex_to_ecdsa_keypair(public: str, private: str) -> ECDSA_256k1_KeyPair:
    return ECDSA_256k1_KeyPair(
        VerifyingKey.from_string(bytes.fromhex(public), curve=ECDSA_CURVE),
        SigningKey.from_string(bytes.fromhex(private), curve=ECDSA_CURVE)
    )
