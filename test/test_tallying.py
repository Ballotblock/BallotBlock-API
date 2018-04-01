#!/usr/bin/env python3
#
# test/test_tallying.py
# Authors:
#   Samuel Vargas
#

import json
import uuid
import unittest
import src.intermediary
from test.config import test_backend
from test.test_util import generate_election_post_data, generate_voter_post_data, ELECTION_DUMMY_RSA_FERNET
from src.httpcode import *
from src.crypto_suite import ECDSAKeyPair
from src.crypto_flow import CryptoFlow
from src.sqlite import SQLiteBackendIO
from src.sessions.session_manager import SessionManager
from src.validator import ElectionJsonValidator
from src.registration import RegistrationServerProvider
from src.time_manager import TimeManager
from unittest.mock import Mock, MagicMock

JSON_HEADERS = {"Content-Type": "application/json"}


class TallyingTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.registration_provider = RegistrationServerProvider()
        self.election_json_validator = ElectionJsonValidator()
        self.session_manager = SessionManager()
        self.time_manager = TimeManager()
        self.election_json_validator.is_valid = MagicMock(return_value=(True, ""))
        self.registration_provider.is_user_registered = MagicMock(return_value=True)
        self.session_manager.is_logged_in = MagicMock(return_value=True)

        # Configurable Election Data
        self.election_creator_ecdsa_keys = ECDSAKeyPair()
        self.username = "ElectionCreator"
        self.election_title = "TallyingTest"
        self.election_description = """
        Verify that we can retreive all ballots and have the system tally them for us
        """

        self.start_date = TimeManager.get_current_time_as_iso_format_string()
        self.end_date = TimeManager.get_current_time_plus_time_delta_in_days_as_iso_8601_str(days=1)
        self.backend = test_backend()

        CryptoFlow.generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict = MagicMock(
            return_value=ELECTION_DUMMY_RSA_FERNET)

        # Setup an election
        self.app = src.intermediary.start_test_sqlite(
            backend_io=self.backend,
            session_manager=self.session_manager,
            election_json_validator=self.election_json_validator,
            registration_provider=self.registration_provider,
            time_manager=self.time_manager
        )

    def setUp(self):
        # Delete all data prior to running the tests
        self.backend.nuke()

        # Generate an election creation post dictionary suitable for sending to the server
        self.election = generate_election_post_data(
            election_title=self.election_title,
            description=self.election_description,
            start_date=self.start_date,
            end_date=self.end_date,
            creator_keys=self.election_creator_ecdsa_keys,
            questions=[
                ["Red or Blue?", ["Red", "Blue"]],
                ["Triangle, Square, Circle, Trapezoid?", ["Triangle", "Square", "Circle", "Trapezoid"]]
            ]
        )

        # Mock ourselves in the system as an Election Creator and send the request
        self.session_manager.get_username = MagicMock(return_value=self.username)
        self.session_manager.election_creator_is_logged_in = MagicMock(return_value=True)
        self.session_manager.voter_is_logged_in = MagicMock(return_value=False)
        response = self.app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(self.election))
        assert response.data.decode('utf-8') == ELECTION_CREATED_SUCCESSFULLY.message
        assert response.status_code == ELECTION_CREATED_SUCCESSFULLY.code

        self.voters = [
            {"username": "Alice", "answers": ["Red", "Triangle"]},
            {"username": "Bob", "answers": ["Red", "Square"]},
            {"username": "Charlie", "answers": ["Blue", "Circle"]},
            {"username": "Doug", "answers": ["Blue", "Circle"]}, # Nobody voted for Trapezoid!
        ]

        # Vote as the above four people in this election.
        for person in self.voters:
            # Generate ECDSA keys so we can sign.
            person['keys'] = ECDSAKeyPair()

            # Generate a ballot
            person['ballot'] = generate_voter_post_data(
                election_title=self.election_title,
                voter_keys=person['keys'],
                answers=person['answers']
            )
            # Mock login as that person
            self.session_manager.election_creator_is_logged_in = MagicMock(return_value=False)
            self.session_manager.voter_is_logged_in = MagicMock(return_value=True)
            self.session_manager.get_username = MagicMock(return_value=person['username'])

            # Cast a vote as this person!
            response = self.app.post("/api/election/vote", headers=JSON_HEADERS, data=json.dumps(person['ballot']))
            voter_uuid = response.data.decode('utf-8')
            uuid.UUID(voter_uuid, version=4) # Ensure that the server returned a voter_uuid

            # Record each person's UUID so we can tie them back to their vote in the ballot data
            person['voter_uuid'] = voter_uuid

    def test_all_four_ballots_are_retrieved_encrypted(self):
        response = self.app.get("/api/ballot/all", data=json.dumps({'election_title': self.election_title}))
        all_ballots = json.loads(response.data.decode('utf-8'))

        for person in self.voters:
            uuid_found = False
            for ballot in all_ballots:
                if ballot['voter_uuid'] == person['voter_uuid']:
                    uuid_found = True
                    assert person['ballot'] != ballot['ballot'] # The text shouldn't be identical if it's encrypted

            assert uuid_found, "UUID: {0} was returned when this person casted their vote but isn't" \
                               "present in the total list!".format(person['voter_uuid'])

    def test_all_four_ballots_are_retrieved_decrypted_after_election_ends(self):
        self.time_manager.election_in_progress = MagicMock(return_value=False)
        response = self.app.get("/api/ballot/all", data=json.dumps({'election_title': self.election_title}))
        all_ballots = json.loads(response.data.decode('utf-8'))

        for person in self.voters:
            uuid_found = False
            for ballot in all_ballots:
                if ballot['voter_uuid'] == person['voter_uuid']:
                    uuid_found = True
                    # ['ballot']['ballot'] is gross should fix soon.
                    # The decrypted string should be identical to what was sent.
                    assert person['ballot']['ballot'] == ballot['ballot']

                    CryptoFlow.verify_data_is_signed_ecdsa(
                        data= ballot['ballot'],
                        string_signature_b64=ballot['ballot_signature'],
                        user_public_key_ecdsa_b64=person['keys'].get_public_key_b64()
                    )

            assert uuid_found, "UUID: {0} was returned when this person casted their vote but isn't" \
                               "present in the total list!".format(person['voter_uuid'])

    def test_tallying_election_adds_answers_correctly(self):
        self.time_manager.election_in_progress = Mock(return_value=False)
        response = self.app.get("/api/election/tally", data=json.dumps({'election_title': self.election_title}))
        tally_results = json.loads(response.data.decode('utf-8'))
        # TODO: Don't hardcode so much in this test
        assert(tally_results['participant_count'] == 4)
        assert(tally_results['questions'][0]["Red or Blue?"]['Blue'] == 2)
        assert(tally_results['questions'][0]["Red or Blue?"]['Red'] == 2)
        assert(tally_results['questions'][1]['Triangle, Square, Circle, Trapezoid?']['Circle'] == 2)
        assert(tally_results['questions'][1]['Triangle, Square, Circle, Trapezoid?']['Square'] == 1)
        assert(tally_results['questions'][1]['Triangle, Square, Circle, Trapezoid?']['Triangle'] == 1)
        assert(tally_results['questions'][1]['Triangle, Square, Circle, Trapezoid?']['Trapezoid'] == 0)

