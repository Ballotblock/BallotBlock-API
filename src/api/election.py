#
#  src/api/election.py
#  Authors:
#       Samuel Vargas
#

from flask import Blueprint, request, jsonify
from src import httpcode, required_keys
from src.settings import SETTINGS
from src.crypto_flow import CryptoFlow
from src.account_types import AccountType
from src.authentication_cookie import AuthenticationCookie
from src.time_manager import TimeManager
import json

election = Blueprint("election", __name__)


@election.route("/api/election/create", methods=["POST"])
def election_create() -> httpcode.HttpCode:
    """
    Allows an election creator to create a new election on the backend.

    See integration/test_create_election.py and
    test/test_election_json_validator.py for details
    about the expected json election format.
    """

    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS['SHARED_PASSWORD'], request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Check if a voter is logged in, report an error if they are
    if AuthenticationCookie.get_account_type(request.cookies) == AccountType.voter:
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

    # Verify an election with this name does not already exist
    if SETTINGS['BACKEND_IO'].get_election_by_title(master_ballot["election_title"]) is not None:
        return httpcode.ELECTION_WITH_TITLE_ALREADY_EXISTS

    # Verify that the election creator correctly signed their 'master_ballot_signature' using
    # their 'creator_public_key'
    if not CryptoFlow.verify_data_is_signed_ecdsa(
            content['master_ballot'],
            content['master_ballot_signature'],
            content['creator_public_key']
    ):
        return httpcode.ELECTION_BALLOT_SIGNING_MISMATCH

    election_crypto = CryptoFlow.generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict()
    master_ballot['questions'] = json.dumps(master_ballot['questions'])
    SETTINGS['BACKEND_IO'].create_election(
        master_ballot,
        creator_username=AuthenticationCookie.get_username(request.cookies),
        creator_master_ballot_signature=content['master_ballot_signature'],
        creator_public_key_b64=content['creator_public_key'],
        election_private_rsa_key=election_crypto['election_private_key'],
        election_public_rsa_key=election_crypto['election_public_key'],
        election_encrypted_fernet_key=election_crypto['election_encrypted_fernet_key']
    )

    return httpcode.ELECTION_CREATED_SUCCESSFULLY

    # Election Encryption Workflow:
    # 1) Generate an RSAKeyPair
    # 2) Generate a FernetObject (each contains a random symmetric key)
    # 3) Encrypt the random symmetric key using the RSAKeyPair (public key)
    # 4) Stick the private key, public key, and encrypted fernet key into the database


# TODO: This is an EXACT search method, the title has to be the same
#       or the search will fail. Modify it to be an actual search function that
#       returns a list of potential elections

@election.route("/api/election/get_by_title", methods=["GET"])
def election_get_by_title():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS["SHARED_PASSWORD"], request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Check if any JSON was supplied at all
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # Verify election_key is present
    for key in required_keys.REQUIRED_ELECTION_SEARCH_BY_TITLE_KEYS:
        if key not in content:
            return httpcode.ELECTION_SEARCH_BY_TITLE_MISSING_ELECTION_TITLE

    # Check if the election was found.
    result = SETTINGS['BACKEND_IO'].get_election_by_title(content["election_title"])
    if result is None:
        return httpcode.ELECTION_NOT_FOUND

    # Remove the private_key if the election hasn't ended yet.
    if TimeManager.election_in_progress(result["start_date"], result['end_date']):
        result.pop('election_private_key')

    return jsonify(result), 200

@election.route("/api/election/past", methods=["GET"])
def get_past_elections():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS["SHARED_PASSWORD"], request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Retrieve all elections
    all_elections = SETTINGS["BACKEND_IO"].get_all_elections()

    # Remove any election from the list that fails the test
    pruned = [
        election for election in all_elections
        if TimeManager.election_in_past(election['end_date'])
    ]

    return jsonify(pruned), 200


@election.route("/api/election/present", methods=["GET"])
def get_present_elections():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS["SHARED_PASSWORD"], request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Retrieve all elections
    all_elections = SETTINGS["BACKEND_IO"].get_all_elections()

    # Remove any election from the list that fails the test
    pruned = [
        election for election in all_elections
        if TimeManager.election_in_progress(election["start_date"], election['end_date'])
    ]

    return jsonify(pruned), 200


@election.route("/api/election/future", methods=["GET"])
def get_future_elections():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS["SHARED_PASSWORD"], request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Retrieve all elections
    all_elections = SETTINGS["BACKEND_IO"].get_all_elections()

    # Remove any election from the list that fails the test
    pruned = [
        election for election in all_elections
        if TimeManager.election_in_future(election["start_date"])
    ]

    return jsonify(pruned), 200
