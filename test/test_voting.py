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

JSON_HEADERS = {"Content-Type": "application/json"}


#
# TODO: Mock out the public private key generation
#

class VotingTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.registration_provider = RegistrationServerProvider()
        self.election_json_validator = ElectionJsonValidator()
        self.session_manager = SessionManager()
        self.election_json_validator.is_valid = MagicMock(return_value=(True, ""))
        self.registration_provider.is_user_registered = MagicMock(return_value=True)
        self.session_manager.is_logged_in = MagicMock(return_value=True)

    def test_voter_can_vote_in_election(self):
        app = src.intermediary.start_test_sqlite(
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
        election = generate_election_post_data(
            election_title="test_voter_can_vote_in_election",
            description="""This election is a test that allows us to
                            to verify that a user can vote in a given
                            election""",
            start_date=int(time.time()),
            end_date=int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()),
            creator_keys=election_creator_ecdsa_keys,
            questions=["Red or Blue?", ["Red", "Blue"]]
        )

        # Verify that the election was created
        response = app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(election))
        assert response.data.decode("utf-8") == ELECTION_CREATED_SUCCESSFULLY.message

        # Cast a vote as a voter
        self.session_manager.election_creator_is_logged_in = MagicMock(return_value=False)
        self.session_manager.voter_is_logged_in = MagicMock(return_value=True)
        self.session_manager.get_username = MagicMock(return_value="Test Voter")
        voter_ecdsa_keys = ECDSAKeyPair()
        ballot = generate_voter_post_data(
            election_title="test_voter_can_vote_in_election",
            voter_keys=voter_ecdsa_keys,
            answers=["Red"]
        )

        # Verify that the vote was cast
        response = app.post("/api/election/vote", headers=JSON_HEADERS, data=json.dumps(ballot))
