#!/usr/bin/env python3
#
# test/test_voting.py
# Authors:
#   Samuel Vargas
#

import unittest
from unittest.mock import MagicMock
from test.test_util import generate_election_post_data, generate_voter_post_data
from src.crypto_suite import ECDSAKeyPair
from src.validator import ElectionJsonValidator
from src.registration import RegistrationServerProvider
from src.sqlite import SQLiteBackendIO
from src.sessions.session_manager import SessionManager
from src.httpcode import *
import json
import src.intermediary
import time
import datetime
import uuid

JSON_HEADERS = {"Content-Type": "application/json"}


class VotingTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.registration_provider = RegistrationServerProvider()
        self.election_json_validator = ElectionJsonValidator()
        self.session_manager = SessionManager()
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
        self.start_date = int(time.time())
        self.end_date = int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp())

    def setUp(self):
        self.app = src.intermediary.start_test_sqlite(
            backend_io=SQLiteBackendIO(":memory:"),
            session_manager=self.session_manager,
            election_json_validator=self.election_json_validator,
            registration_provider=self.registration_provider,
        )

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

    def test_voter_can_vote_in_election(self):
        # Cast a vote as a voter
        voter_ecdsa_keys = ECDSAKeyPair()
        ballot = generate_voter_post_data(
            election_title=self.election_title,
            voter_keys=voter_ecdsa_keys,
            answers=["Red"]
        )

        # Verify that the vote was cast
        response = self.app.post("/api/election/vote", headers=JSON_HEADERS, data=json.dumps(ballot))

    def test_voter_can_retrieve_their_ballot_with_returned_voter_uuid(self):
        # Cast a vote as a voter
        voter_ecdsa_keys = ECDSAKeyPair()
        ballot = generate_voter_post_data(
            election_title=self.election_title,
            voter_keys=voter_ecdsa_keys,
            answers=["Red"]
        )

        # Verify that the vote was cast
        response = self.app.post("/api/election/vote", headers=JSON_HEADERS, data=json.dumps(ballot))
        voter_uuid = response.data.decode('utf-8')

        # Verify that the server did return a uuid4
        try:
            uuid.UUID(voter_uuid, version=4)
        except ValueError:
            self.fail("The server should have returned a uuid4!")

        data = json.dumps({'voter_uuid': voter_uuid})
        response = self.app.post("/api/ballot/get", headers=JSON_HEADERS, data=data)
        retrieved_ballot = json.loads(response.data)

        assert retrieved_ballot["election_title"] == self.election_title
        assert retrieved_ballot["voter_uuid"] == voter_uuid
