# !/usr/bin/env python3
#
# Path modification trick to allow you to execute the program
# using either:
#     * python -m src.intermediary
#     * python intermediary.py

import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

# Subdirectories
SUBDIRECTORIES = [
    "..",
    "interfaces",
    "sqlite3",
]

for subdirectory in SUBDIRECTORIES:
    sys.path.append(os.path.join(dir_path, subdirectory))

#
# src/intermediary.py
# Authors:
#     Samuel Vargas
#     Alex Gao

from flask import Flask, request, jsonify, session
from src import httpcode
from src.validator import ElectionJsonValidator
from src.sessions import SessionManager
from src.registration import RegistrationServerProvider
from src.interfaces import BackendIO
from src import required_keys
from src.crypto_suite import ECDSAKeyPair, FernetCrypt, RSAKeyPair
from src.crypto_flow import verify_data_is_signed_ecdsa
import json
import uuid
import time
import base64

app = Flask(__name__)

URL = "0.0.0.0"
DEBUG_URL = "127.0.0.1"
NAME = "BallotBlock API"
PORT = 8080

# Modules
BACKEND_IO = None
SESSION_MANAGER = SessionManager()
REGISTRATION_PROVIDER = RegistrationServerProvider()
ELECTION_JSON_VALIDATOR = ElectionJsonValidator()

app.config['SECRET_KEY'] = str(uuid.uuid4())
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False


def start_test_sqlite(backend_io: BackendIO = None,
                      session_manager=SessionManager(),
                      registration_provider=RegistrationServerProvider(),
                      election_json_validator=ElectionJsonValidator()
                      ):
    if backend_io is None:
        raise ValueError("backend_io can't be none")

    global BACKEND_IO
    global SESSION_MANAGER
    global REGISTRATION_PROVIDER
    global ELECTION_JSON_VALIDATOR

    BACKEND_IO = backend_io
    SESSION_MANAGER = session_manager
    REGISTRATION_PROVIDER = registration_provider
    ELECTION_JSON_VALIDATOR = election_json_validator

    test_app = app.test_client()
    test_app.testing = True
    return test_app


#
# Login
#

@app.route("/api/login", methods=["GET", "POST"])
def login() -> httpcode.HttpCode:
    # JSON is missing or malformed
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # At least one required login parameter is missing
    for key in content:
        if key not in required_keys.REQUIRED_LOGIN_KEYS:
            return httpcode.MISSING_LOGIN_PARAMETERS

    # The registration server says this user is invalid:
    if not REGISTRATION_PROVIDER.is_user_registered(content['username'], content['password']):
        return httpcode.USER_NOT_REGISTERED

    # The user is already authenticated
    if SESSION_MANAGER.is_logged_in(session):
        return httpcode.USER_ALREADY_AUTHENTICATED

    # The user is not already authenticated, authenticate them and return OK
    SESSION_MANAGER.login(content['username'], content["account_type"], session)
    return httpcode.LOGIN_SUCCESSFUL


#
# Elections
#

@app.route("/api/election/create", methods=["POST"])
def election_create() -> httpcode.HttpCode:
    """
    Allows an election creator to create a new election on the backend.

    See integration/test_create_election.py and
    test/test_election_json_validator.py for details
    about the expected json election format.
    """

    # Check if anyone is logged in
    if not SESSION_MANAGER.is_logged_in(session):
        return httpcode.LOG_IN_FIRST

    # Check if a voter is logged in, report an error if they are
    if SESSION_MANAGER.voter_is_logged_in(session):
        return httpcode.VOTER_CANNOT_CREATE_ELECTION

    # Check if any JSON was supplied at all
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # Verify that master_ballot, public_key, and signature are present
    for key in required_keys.REQUIRED_ELECTION_KEYS:
        if key not in content:
            return httpcode.ELECTION_MISSING_BALLOT_PUBLIC_KEY_OR_SIGNATURE

    # Verify that master_ballot is a valid JSON string
    try:
        master_ballot = json.loads(content['master_ballot'])
    except ValueError:
        return httpcode.ELECTION_BALLOT_JSON_MALFORMED

    # Verify that master_ballot contains all the required keys
    for key in required_keys.REQUIRED_ELECTION_MASTER_BALLOT_KEYS:
        if key not in master_ballot:
            return httpcode.ELECTION_BALLOT_MISSING_TITLE_DESCRIPTION_DATE_OR_QUESTIONS

    # TODO: Verify that the master_ballot itself contains valid data only!
    valid, reason = ELECTION_JSON_VALIDATOR.is_valid(master_ballot)
    if not valid:
        return reason

    # Verify an election with this name does not already exist
    if BACKEND_IO.get_election_by_title(master_ballot["election_title"]) is not None:
        return httpcode.ELECTION_WITH_TITLE_ALREADY_EXISTS

    # Verify that the election creator correctly signed their 'master_ballot_signature' using
    # their 'creator_public_key'
    if not verify_data_is_signed_ecdsa(
            content['master_ballot'],
            content['master_ballot_signature'],
            content['creator_public_key']
    ):
        return httpcode.ELECTION_BALLOT_SIGNING_MISMATCH

    # Election Encryption Workflow:
    # 1) Generate an RSAKeyPair
    # 2) Generate a FernetObject (each contains a random symmetric key)
    # 3) Encrypt the random symmetric key using the RSAKeyPair (public key)
    # 4) Stick the private key, public key, and encrypted fernet key into the database

    election_rsa = RSAKeyPair()
    election_fernet = FernetCrypt()
    election_encrypted_fernet_key = election_rsa.encrypt_message_as_b64(election_fernet.get_key_as_bytes())

    master_ballot['questions'] = json.dumps(master_ballot['questions'])
    BACKEND_IO.create_election(
        master_ballot,
        creator_username=SESSION_MANAGER.get_username(session),
        creator_master_ballot_signature=content['master_ballot_signature'],
        creator_public_key_b64=content['creator_public_key'],
        election_private_rsa_key=election_rsa.get_private_key_as_pkcs1_b64(),
        election_public_rsa_key=election_rsa.get_public_key_as_pkcs1_b64(),
        election_encrypted_fernet_key=election_encrypted_fernet_key
    )

    return httpcode.ELECTION_CREATED_SUCCESSFULLY


# TODO: This is an EXACT search method, the title has to be the same
#       or the search will fail. Modify it to be an actual search function that
#       returns a list of potential elections

@app.route("/api/election/get_by_title", methods=["GET"])
def election_get_by_title():
    # Check if anyone is logged in
    if not SESSION_MANAGER.is_logged_in(session):
        return httpcode.LOG_IN_FIRST

    # Check if any JSON was supplied at all
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # Verify election_key is present
    for key in required_keys.REQUIRED_ELECTION_SEARCH_BY_TITLE_KEYS:
        if key not in content:
            return httpcode.ELECTION_SEARCH_BY_TITLE_MISSING_ELECTION_TITLE

    # Check if the election was found.
    result = BACKEND_IO.get_election_by_title(content["election_title"])
    if result is None:
        return httpcode.ELECTION_NOT_FOUND

    # Remove the private_key if the election hasn't ended yet.
    if int(time.time()) < result['end_date']:
        result.pop('election_private_key')

    return jsonify(result), 200


@app.route("/api/election/vote", methods=["GET", "POST"])
def election_cast_vote():
    # Check if anyone is logged in
    if not SESSION_MANAGER.is_logged_in(session):
        return httpcode.LOG_IN_FIRST

    # Check if any JSON was supplied at all
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # Verify that 'public_key', 'ballot', and 'ballot_signature' were provided
    for key in required_keys.REQUIRED_ELECTION_VOTE_KEYS:
        if key not in content:
            return httpcode.ELECTION_VOTER_BALLOT_MISSING_BALLOT_PUBLIC_KEY_OR_SIGNATURE

    # Verify that 'ballot' is valid JSON
    try:
        ballot = json.loads(content['ballot'])
    except ValueError:
        return httpcode.ELECTION_VOTER_BALLOT_JSON_IS_MALFORMED

    # Verify that the 'election_title' and 'answers' were provided in the ballot
    for key in required_keys.REQUIRED_ELECTION_VOTE_BALLOT_KEYS:
        if key not in ballot:
            return httpcode.ELECTION_VOTER_BALLOT_MISSING_BALLOT_PUBLIC_KEY_OR_SIGNATURE

    # Verify that this election actually exists
    election = BACKEND_IO.get_election_by_title(ballot['election_title'])
    if election is None:
        return httpcode.ELECTION_NOT_FOUND

    # TODO: Verify that the provided answers match the question options!
    # TODO: Verify that the election hasn't ended already

    # Verify that the user signed their ballot data correctly
    if not verify_data_is_signed_ecdsa(
            content['ballot'],
            content['ballot_signature'],
            content['voter_public_key']
    ):
        return httpcode.ELECTION_BALLOT_SIGNING_MISMATCH

    # Fetch the RSA Key from the ballot's corresponding election
    election_rsa = RSAKeyPair(
        use_public_pkcs1_b64_key=election["election_public_key"].decode('utf-8'),
        use_private_pkcs1_b64_key=election["election_private_key"].decode('utf-8')
    )

    # Decrypt the fernet symmetric key
    decrypted_fernet_key = election_rsa.decrypt_b64_to_bytes(election["election_encrypted_fernet_key"])
    fernet_crypt = FernetCrypt(
        use_fernet_key_bytes=decrypted_fernet_key
    )

    # Encrypt the user's ballot using our decrypted symmetric fernet key
    encrypted_ballot = fernet_crypt.encrypt_to_b64(content["ballot"].encode('utf-8')).decode('utf-8')

    voter_uuid = str(uuid.uuid4())

    BACKEND_IO.create_ballot(
        encrypted_ballot,
        election_title = election['election_title'],
        voter_uuid=voter_uuid,
        ballot_signature=content['ballot_signature'],
        voter_public_key_b64=content['voter_public_key'],
    )

    return str(voter_uuid), 201
