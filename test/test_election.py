#!/usr/bin/env python3
#
# test/test_election.py
# Authors:
#   Samuel Vargas
#

import json
import uuid
import unittest
import datetime
import time
import src.intermediary
from test.test_util import generate_election_post_data, generate_voter_post_data
from src.httpcode import *
from src.crypto_suite import ECDSAKeyPair
from src.sqlite import SQLiteBackendIO
from src.sessions.session_manager import SessionManager
from src.validator import ElectionJsonValidator
from src.registration import RegistrationServerProvider
from unittest.mock import MagicMock

JSON_HEADERS = {"Content-Type": "application/json"}


class ElectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.registration_provider = RegistrationServerProvider()
        self.election_json_validator = ElectionJsonValidator()
        self.session_manager = SessionManager()
        self.election_json_validator.is_valid = MagicMock(return_value=(True, ""))
        self.registration_provider.is_user_registered = MagicMock(return_value=True)
        self.session_manager.is_logged_in = MagicMock(return_value=True)

    def test_election_creator_can_create_election(self):
        username = "Test Election Creator"
        account_type = "ElectionCreator"
        election_creator_ecdsa_keys = ECDSAKeyPair()

        app = src.intermediary.start_test_sqlite(
            backend_io=SQLiteBackendIO(":memory:"),
            session_manager=self.session_manager,
            election_json_validator=self.election_json_validator,
            registration_provider=self.registration_provider,
        )

        election = generate_election_post_data(
            election_title="test_election_creator_can_create_single_election",
            description="""This is a test that verifies if an election creator can create
            a single election.""",
            start_date=int(time.time()),
            end_date=int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()),
            creator_keys=election_creator_ecdsa_keys,
            questions=["Red or Blue?", ["Red", "Blue"]])

        response = app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(election))
        assert response.data.decode('utf-8') == ELECTION_CREATED_SUCCESSFULLY.message
        assert response.status_code == ELECTION_CREATED_SUCCESSFULLY.code
