#!/usr/bin/env python3
#
# src/key.py
# Authors:
#   Samuel Vargas
#

from typing import NamedTuple
from collections import namedtuple
import ecdsa
from ecdsa import SigningKey, VerifyingKey

ECDSA_CURVE = ecdsa.SECP256k1

HexKeyPair = NamedTuple("hexkeypair", [("public", str), ("private", str)])
_hexkeypair = namedtuple("hexkeypair", ("public", "private"))


def generate_edsca_hexkeypair() -> HexKeyPair:
    """
    Generates an EDSCA public private key pair.
    The values are returned as strings for easy
    serialization.

    :return: A HexKeyPair tuple
    """
    private = SigningKey.generate(curve=ECDSA_CURVE)
    public = private.get_verifying_key()
    private_string = (private.to_string()).hex()
    public_string = (public.to_string()).hex()
    return _hexkeypair(public_string, private_string)


def public_hex_to_verifying_key(hex: str) -> VerifyingKey:
    return VerifyingKey.from_string(bytes.fromhex(hex), curve=ECDSA_CURVE)


def private_hex_to_signing_key(hex: str) -> SigningKey:
    return SigningKey.from_string(bytes.fromhex(hex), curve=ECDSA_CURVE)


