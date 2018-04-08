#
#  src/api/tally.py
#  Authors:
#       Samuel Vargas

from flask import Blueprint, request, jsonify
from src import httpcode, required_keys
from src.settings import SETTINGS
from src.crypto_flow import CryptoFlow
from src.authentication_cookie import AuthenticationCookie
from src.time_manager import TimeManager
from src.tally_machine import TallyMachine
import json

tally = Blueprint("tally", __name__)


@tally.route("/api/election/tally", methods=["GET"])
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
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS["SHARED_PASSWORD"], request.cookies):
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
    election = SETTINGS["BACKEND_IO"].get_election_by_title(content['election_title'])
    if election is None:
        return httpcode.ELECTION_NOT_FOUND

    # 4) If the election is still in process return an error
    if TimeManager.election_in_progress(election["start_date"], election['end_date']):
        return httpcode.ELECTION_CANT_TALLY_VOTING_STILL_IN_PROGRESS

    # 5) Request each ballot from the backend (no order is required)
    all_ballots = SETTINGS["BACKEND_IO"].get_all_ballots(content['election_title'])

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
