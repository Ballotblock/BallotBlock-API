#
#  src/api/vote.py
#  Authors:
#       Samuel Vargas
#

from flask import Blueprint, request, jsonify
from src import httpcode, required_keys
from src.settings import SETTINGS
from src.crypto_flow import CryptoFlow
from src.authentication_cookie import AuthenticationCookie
from src.time_manager import TimeManager
import json
import uuid

vote = Blueprint("vote", __name__)

@vote.route("/api/election/vote", methods=["POST"])
def election_cast_vote():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS["SHARED_PASSWORD"], request.cookies):
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
    election = SETTINGS['BACKEND_IO'].get_election_by_title(ballot['election_title'])
    if election is None:
        return httpcode.ELECTION_NOT_FOUND

    # Verify the user has not already participated in this election
    username = AuthenticationCookie.get_username(request.cookies)
    if SETTINGS['BACKEND_IO'].has_user_participated_in_election(username, ballot['election_title']):
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
    SETTINGS['BACKEND_IO'].create_ballot(
        encrypted_ballot,
        election_title=election['election_title'],
        voter_uuid=voter_uuid,
        ballot_signature=content['ballot_signature'],
        voter_public_key_b64=content['voter_public_key'],
    )

    SETTINGS['BACKEND_IO'].register_user_as_participated_in_election(username, ballot['election_title'])

    return str(voter_uuid), 201

@vote.route("/api/ballot/get", methods=["GET", "POST"])
def get_voter_ballot_by_voter_uuid():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS['SHARED_PASSWORD'], request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    # Check if any JSON was supplied at all
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # Verify the voter UUID is present
    if "voter_uuid" not in content:
        return "Missing voter_uuid", 400

    # Ask the backend if this voter exists
    result = SETTINGS['BACKEND_IO'].get_ballot_by_voter_uuid(content['voter_uuid'])
    if result is None:
        return "Could not find a voter_ballot with this uuid", 404

    # Get the corresponding election
    election = SETTINGS['BACKEND_IO'].get_election_by_title(result['election_title'])

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


@vote.route("/api/ballot/all", methods=["GET"])
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
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS["SHARED_PASSWORD"], request.cookies):
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
    election = SETTINGS['BACKEND_IO'].get_election_by_title(content['election_title'])
    if election is None:
        return httpcode.ELECTION_NOT_FOUND

    # 4) Request each ballot from the backend (no order is required)
    all_ballots = SETTINGS['BACKEND_IO'].get_all_ballots(content['election_title'])

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
