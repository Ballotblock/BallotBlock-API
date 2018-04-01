#!/usr/bin/env python3
#
# test/test_voting.py
# Authors:
#   Samuel Vargas
#

import unittest
from test.config import test_backend
from unittest.mock import MagicMock
from test.test_util import generate_election_post_data, generate_voter_post_data, ELECTION_DUMMY_RSA_FERNET
from src.crypto_suite import ECDSAKeyPair
from src.validator import ElectionJsonValidator
from src.registration import RegistrationServerProvider
from src.sqlite import SQLiteBackendIO
from src.sessions.session_manager import SessionManager
from src.crypto_flow import CryptoFlow
from src.time_manager import TimeManager
from src.httpcode import *
import json
import src.intermediary
import time
from datetime import timezone
import datetime
import uuid

JSON_HEADERS = {"Content-Type": "application/json"}


class VotingTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.registration_provider = RegistrationServerProvider()
        self.election_json_validator = ElectionJsonValidator()
        self.session_manager = SessionManager()
        self.time_manager = TimeManager()
        self.election_json_validator.is_valid = MagicMock(return_value=(True, ""))
        self.registration_provider.is_user_registered = MagicMock(return_value=True)
        self.session_manager.is_logged_in = MagicMock(return_value=True)

        # Election Information
        self.election_title = "TestVoting"
        self.election_description = """
            This test exists to verify that:
            1) A user can cast a vote
            2) A user can retrieve their vote from the server
            3) If the election is over the user can decrypt their ballot.
        """
        self.start_date = TimeManager.get_current_time_as_iso_format_string()
        self.end_date = TimeManager.get_current_time_plus_time_delta_in_days_as_iso_8601_str(days=1)
        self.backend = test_backend()

        CryptoFlow.generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict = MagicMock(
            return_value=ELECTION_DUMMY_RSA_FERNET)

        self.app = src.intermediary.start_test_sqlite(
            backend_io=self.backend,
            session_manager=self.session_manager,
            election_json_validator=self.election_json_validator,
            registration_provider=self.registration_provider,
            time_manager=self.time_manager
        )

    def setUp(self):
        # Delete all data prior to running the test
        self.backend.nuke()

        # Create an election as an election creator
        self.session_manager.voter_is_logged_in = MagicMock(return_value=False)
        self.session_manager.election_creator_is_logged_in = MagicMock(return_value=True)
        self.session_manager.get_username = MagicMock(return_value="Test Election Creator")
        election_creator_ecdsa_keys = ECDSAKeyPair()
        self.election = generate_election_post_data(
            election_title=self.election_title,
            description=self.election_description,
            start_date=self.start_date,
            end_date=self.end_date,
            creator_keys=election_creator_ecdsa_keys,
            questions=["Red or Blue?", ["Red", "Blue"]]
        )

        # Verify that the election was created
        response = self.app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(self.election))
        assert response.data.decode("utf-8") == ELECTION_CREATED_SUCCESSFULLY.message

        # Log out as an election creator, log back in as a user
        self.session_manager.election_creator_is_logged_in = MagicMock(return_value=False)
        self.session_manager.voter_is_logged_in = MagicMock(return_value=True)
        self.session_manager.get_username = MagicMock(return_value="Test Voter")

        # Cast a single vote as a voter
        self.voter_ecdsa_keys = ECDSAKeyPair()
        self.ballot = generate_voter_post_data(
            election_title=self.election_title,
            voter_keys=self.voter_ecdsa_keys,
            answers=["Red"]
        )

        # Verify that the vote was cast
        response = self.app.post("/api/election/vote", headers=JSON_HEADERS, data=json.dumps(self.ballot))
        # Will throw and fail test iff server did not return a uuid
        self.voter_uuid = response.data.decode('utf-8')
        uuid.UUID(self.voter_uuid, version=4)

    def test_voter_can_vote_in_election_once(self):
        # Disallow a user from voting twice in the same election.
        # The logged in username is used to detect this.
        response = self.app.post("/api/election/vote", headers=JSON_HEADERS, data=json.dumps(self.ballot))
        assert ELECTION_VOTER_VOTED_ALREADY.message == response.data.decode('utf-8')

    def test_voter_can_retrieve_their_ballot_with_returned_voter_uuid(self):
        # Verify that the correct data is retrieved from the backend.
        data = json.dumps({'voter_uuid': self.voter_uuid})
        response = self.app.post("/api/ballot/get", headers=JSON_HEADERS, data=data)
        retrieved_ballot = json.loads(response.data)

        assert retrieved_ballot["election_title"] == self.election_title
        assert retrieved_ballot["voter_uuid"] == self.voter_uuid

    def test_voter_can_verify_ecdsa_signature_during_election(self):
        self.time_manager.election_in_progress = MagicMock(return_value=True)
        data = json.dumps({'voter_uuid': self.voter_uuid})
        response = self.app.post("/api/ballot/get", headers=JSON_HEADERS, data=data)
        ballot_signature = json.loads(response.data)['ballot_signature']
        assert self.voter_ecdsa_keys.is_signed(ballot_signature.encode('utf-8'), self.ballot['ballot'].encode('utf-8'))

    def test_voter_cannot_see_decrypted_ballot_during_election(self):
        # Mock the test so that the election is still in progress
        self.time_manager.election_in_progress = MagicMock(return_value=True)
        # Verify that the ballot data is encrypted (not identical) to the submitted ballot data
        data = json.dumps({'voter_uuid': self.voter_uuid})
        response = self.app.post("/api/ballot/get", headers=JSON_HEADERS, data=data)
        retrieved_ballot = json.loads(response.data)
        assert retrieved_ballot['ballot'] != self.ballot['ballot']

    def test_voter_can_retrieve_decrypted_ballot_when_election_is_over(self):
        # Mock the test so that it's over!
        self.time_manager.election_in_progress = MagicMock(return_value=False)

        # Verify that the ballot data is decrypted (identical) to the submitted ballot data
        data = json.dumps({'voter_uuid': self.voter_uuid})
        response = self.app.post("/api/ballot/get", headers=JSON_HEADERS, data=data)
        retrieved_ballot = json.loads(response.data)
        assert retrieved_ballot['ballot'] == self.ballot['ballot']
