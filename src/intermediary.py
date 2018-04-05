# !/usr/bin/env python3
# src/intermediary.py
# Authors:
#     Samuel Vargas
#     Alex Gao

from flask import Flask, request, jsonify, session
from src import httpcode
from src.validator import ElectionJsonValidator
from src.authentication_cookie import AuthenticationCookie
from src.interfaces import BackendIO
from src import required_keys
from src.crypto_flow import CryptoFlow
from src.time_manager import TimeManager
from src.tally_machine import TallyMachine
from src.account_types import AccountType
import json
import uuid

app = Flask(__name__)

URL = "0.0.0.0"
NAME = "BallotBlock API"
PORT = 8080
BACKEND_IO = None
SHARED_PASSWORD = "BallotBlockDefaultPassword" # Change this prior to deploying system.

app.config['SECRET_KEY'] = str(uuid.uuid4())
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False


def start_test(backend_io: BackendIO, shared_password: str = None):
    assert backend_io, "'backend_io' cannot be None"
    global BACKEND_IO

    # Setup BackendIO
    BACKEND_IO = backend_io

    # Setup Password
    if shared_password:
        global SHARED_PASSWORD
        SHARED_PASSWORD = shared_password

    test_app = app.test_client()
    test_app.testing = True
    return test_app

#
#
#
@app.route("/api/authentication", methods=["POST"])
def cookie_has_valid_authentication():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    return httpcode.VALID_AUTHENTICATION_COOKIE



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

    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
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
    valid, reason = ElectionJsonValidator.is_valid(master_ballot)
    if not valid:
        return reason

    # Verify an election with this name does not already exist
    if BACKEND_IO.get_election_by_title(master_ballot["election_title"]) is not None:
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
    BACKEND_IO.create_election(
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

@app.route("/api/election/get_by_title", methods=["GET"])
def election_get_by_title():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
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
    result = BACKEND_IO.get_election_by_title(content["election_title"])
    if result is None:
        return httpcode.ELECTION_NOT_FOUND

    # Remove the private_key if the election hasn't ended yet.
    if TimeManager.election_in_progress(result["start_date"], result['end_date']):
        result.pop('election_private_key')

    return jsonify(result), 200


@app.route("/api/election/vote", methods=["POST"])
def election_cast_vote():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

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

    # Verify the user has not already participated in this election
    username = AuthenticationCookie.get_username(request.cookies)
    if BACKEND_IO.has_user_participated_in_election(username, ballot['election_title']):
        return httpcode.ELECTION_VOTER_VOTED_ALREADY

    # Verify that the election is still in progress
    if not TimeManager.election_in_progress(election['start_date'], election['end_date']):
        return httpcode.ELECTION_IS_INACTIVE

    # TODO: Verify that the provided answers match the question options!

    # Verify that the user signed their ballot data correctly
    if not CryptoFlow.verify_data_is_signed_ecdsa(
            content['ballot'],
            content['ballot_signature'],
            content['voter_public_key']
    ):
        return httpcode.ELECTION_BALLOT_SIGNING_MISMATCH

    # Decrypt the encrypted Fernet key and then encrypt the user's ballot with the Fernet key
    encrypted_ballot = CryptoFlow.encrypt_vote_with_election_creator_rsa_keys_and_encrypted_fernet_key(
        ballot_str=content['ballot'],
        rsa_private_key_b64=election["election_private_key"],
        rsa_public_key_b64=election["election_public_key"],
        encrypted_fernet_key=election["election_encrypted_fernet_key"]
    )

    # Generate a per election voter UUID so the user can retrieve this ballot again.
    voter_uuid = str(uuid.uuid4())
    BACKEND_IO.create_ballot(
        encrypted_ballot,
        election_title=election['election_title'],
        voter_uuid=voter_uuid,
        ballot_signature=content['ballot_signature'],
        voter_public_key_b64=content['voter_public_key'],
    )

    BACKEND_IO.register_user_as_participated_in_election(username, ballot['election_title'])

    return str(voter_uuid), 201


@app.route("/api/ballot/get", methods=["GET", "POST"])
def get_voter_ballot_by_voter_uuid():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Check if any JSON was supplied at all
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # Verify the voter UUID is present
    if "voter_uuid" not in content:
        return "Missing voter_uuid", 400

    # Ask the backend if this voter exists
    result = BACKEND_IO.get_ballot_by_voter_uuid(content['voter_uuid'])
    if result is None:
        return "Could not find a voter_ballot with this uuid", 404

    # Get the corresponding election
    election = BACKEND_IO.get_election_by_title(result['election_title'])

    # If the election has ended, decrypt the users ballot and return
    # that instead.
    if not TimeManager.election_in_progress(election["start_date"], election['end_date']):
        result['ballot'] = CryptoFlow.decrypt_ballot(
            encrypted_ballot_str=result['ballot'],
            election_rsa_public_key_b64=election['election_public_key'],
            election_rsa_private_key_b64=election['election_private_key'],
            election_encrypted_fernet_key_b64=election['election_encrypted_fernet_key'],
        )

    # Return the found content
    return jsonify(result), 200


@app.route("/api/ballot/all", methods=["GET"])
def get_all_ballots_in_election():
    """
    Expects a JSON object to be sent with the following format:

    {
        "election_title", "Election_Title"
    }

    :return: Either ELECTION_NOT_FOUND or a JSON object with
             the following format:
             [
                {
                  "voter_uuid": "This voter's uuid",
                  "ballot": "Encrypted data OR the user's unencrypted ballot as a json string
                  "ballot_signature": "The ballot signature"
                  "election_title": "Title of the election",
                },

                { 'answers': '['Red', 'Triangle']'
                  "voter_uuid" :
                  "ballot" :
                  "ballot_signature" :
                  "election_title" :
                },

                ...
             ]
    """

    # TODO: Return an error if the election hasn't started yet.

    # 0) Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # 1) Check if any JSON was supplied at all
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # 2) Verify that the "election_title" key was provided
    for key in required_keys.REQUIRED_ELECTION_GET_ALL_BALLOTS_KEYS:
        if key not in content:
            return "Missing key: '{0}' in sent JSON".format(key), 400

    # 3) Verify that the election actually exists
    election = BACKEND_IO.get_election_by_title(content['election_title'])
    if election is None:
        return httpcode.ELECTION_NOT_FOUND

    # 4) Request each ballot from the backend (no order is required)
    all_ballots = BACKEND_IO.get_all_ballots(content['election_title'])

    # 5) If the election is over, decrypt all ballots.
    if not TimeManager.election_in_progress(election["start_date"], election['end_date']):
        for ballot in all_ballots:
            ballot['ballot'] = CryptoFlow.decrypt_ballot(
                encrypted_ballot_str=ballot['ballot'],
                election_rsa_public_key_b64=election['election_public_key'],
                election_rsa_private_key_b64=election['election_private_key'],
                election_encrypted_fernet_key_b64=election['election_encrypted_fernet_key'],
            )

    # 6) Convert it to JSON and return it to the user, indicate 200 for OK
    return jsonify(all_ballots), 200


@app.route("/api/election/tally", methods=["GET"])
def tally_results_for_given_election():
    """
    Accepts a JSON object in the format:
    {
        "election_title": "Whatever the election title is.
    }

    :return: A JSON object with the format:
                 {
                    "participant_count" : 48
                    "questions" :
                    [
                        {
                        "Favorite Color?" :
                            {
                                "Red" : 32
                                "Blue" : 16
                            },
                        },

                        {
                        "Favorite SHape?" :
                            {
                                "Triangle" : 40
                                "Square" : 8
                            },
                        },


                        ....

                     ]
                 }
    """
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # 1) Check if any JSON was supplied at all
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # 2) Verify that the "election_title" key was provided
    for key in required_keys.REQUIRED_ELECTION_TALLY_RESULTS_KEYS:
        if key not in content:
            return "Missing key: '{0}' in sent JSON".format(key), 400

    # 3) Verify that the election actually exists
    election = BACKEND_IO.get_election_by_title(content['election_title'])
    if election is None:
        return httpcode.ELECTION_NOT_FOUND

    # 4) If the election is still in process return an error
    if TimeManager.election_in_progress(election["start_date"], election['end_date']):
        return httpcode.ELECTION_CANT_TALLY_VOTING_STILL_IN_PROGRESS

    # 5) Request each ballot from the backend (no order is required)
    all_ballots = BACKEND_IO.get_all_ballots(content['election_title'])

    # 6) Decrypt each ballot.
    for ballot in all_ballots:
        ballot['ballot'] = CryptoFlow.decrypt_ballot(
            encrypted_ballot_str=ballot['ballot'],
            election_rsa_public_key_b64=election['election_public_key'],
            election_rsa_private_key_b64=election['election_private_key'],
            election_encrypted_fernet_key_b64=election['election_encrypted_fernet_key'],
        )

    # 7) Calculate and return the results of the election
    questions = json.loads(election['questions'])

    result = TallyMachine.tally_election_ballots(questions, all_ballots)
    return jsonify(result), 200


@app.route("/api/election/past", methods=["GET"])
def get_past_elections():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Retrieve all elections
    all_elections = BACKEND_IO.get_all_elections()

    # Remove any election from the list that fails the test
    pruned = [
        election for election in all_elections
        if TimeManager.election_in_past(election['end_date'])
    ]

    return jsonify(pruned), 200


@app.route("/api/election/present", methods=["GET"])
def get_present_elections():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Retrieve all elections
    all_elections = BACKEND_IO.get_all_elections()

    # Remove any election from the list that fails the test
    pruned = [
        election for election in all_elections
        if TimeManager.election_in_progress(election["start_date"], election['end_date'])
    ]

    return jsonify(pruned), 200


@app.route("/api/election/future", methods=["GET"])
def get_future_elections():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SHARED_PASSWORD, request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Retrieve all elections
    all_elections = BACKEND_IO.get_all_elections()

    # Remove any election from the list that fails the test
    pruned = [
        election for election in all_elections
        if TimeManager.election_in_future(election["start_date"])
    ]

    return jsonify(pruned), 200
