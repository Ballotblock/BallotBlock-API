#!/usr/bin/env python3
#
# test/test_election.py
# Authors:
#   Samuel Vargas
#

import json
import unittest
import src.intermediary
from test.config import test_backend
from test.dummy_keys import *
from test.test_util import generate_election_post_data, generate_voter_post_data, ELECTION_DUMMY_RSA_FERNET
from src.httpcode import *
from src.crypto_suite import ECDSAKeyPair
from src.crypto_flow import CryptoFlow
from src.sqlite import SQLiteBackendIO
from src.sessions.session_manager import SessionManager
from src.validator import ElectionJsonValidator
from src.registration import RegistrationServerProvider
from src.time_manager import TimeManager
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

JSON_HEADERS = {"Content-Type": "application/json"}


class ElectionPastPresentFutureTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.registration_provider = RegistrationServerProvider()
        self.election_json_validator = ElectionJsonValidator()
        self.session_manager = SessionManager()
        self.time_manager = TimeManager()

        # Mock out election validation (currently not undertest)
        self.election_json_validator.is_valid = MagicMock(return_value=(True, ""))
        self.registration_provider.is_user_registered = MagicMock(return_value=True)
        self.session_manager.is_logged_in = MagicMock(return_value=True)

        # Election Data
        self.election_creator_ecdsa_keys = ECDSAKeyPair()
        self.username = "ElectionCreator"
        self.election_title = "ElectionPastPresentFutureTest"
        self.election_description = "Test that we can retrieve elections via their start / end dates."

        self.backend = test_backend()
        self.start_date = TimeManager.get_current_time_as_iso_format_string()
        self.end_date = TimeManager.get_current_time_plus_time_delta_in_days_as_iso_8601_str(days=1)

        # Setup testing app
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

        self.election = generate_election_post_data(
            election_title=self.election_title,
            description=self.election_description,
            start_date=self.start_date,
            end_date=self.end_date,
            creator_keys=self.election_creator_ecdsa_keys,
            questions=["Red or Blue?", ["Red", "Blue"]])

        elections = [
            {"election_title": "Past Election 1",
             "description": "...",
             "start_date": datetime(2000, 1, 1).isoformat(),
             "end_date": datetime(2000, 1, 2).isoformat(),
             "creator_keys": ECDSAKeyPair(),
             "questions": ["Don't Care", ["Don't", "Care"]],
             "stub_rsa": ELECTION_DUMMY_RSA_FERNET_ONE
             },

            {"election_title": "Past Election 2",
             "description": "...",
             "start_date": datetime(2000, 1, 1, tzinfo=timezone.utc).isoformat(),
             "end_date": datetime(2000, 1, 2, tzinfo=timezone.utc).isoformat(),
             "creator_keys": ECDSAKeyPair(),
             "questions": ["Don't Care", ["Don't", "Care"]],
             "stub_rsa": ELECTION_DUMMY_RSA_FERNET_TWO
             },

            {"election_title": "Present Election 1",
             "description": "...",
             "start_date": datetime.now(timezone.utc).astimezone().isoformat(),
             "end_date": (datetime.now(timezone.utc).astimezone() + timedelta(days=1)).isoformat(),
             "creator_keys": ECDSAKeyPair(),
             "questions": ["Don't Care", ["Don't", "Care"]],
             "stub_rsa": ELECTION_DUMMY_RSA_FERNET_THREE
             },

            {"election_title": "Present Election 2",
             "description": "...",
             "start_date": datetime.now(timezone.utc).isoformat(),
             "end_date": (datetime.now(timezone.utc).astimezone() + timedelta(days=1)).isoformat(),
             "creator_keys": ECDSAKeyPair(),
             "questions": ["Don't Care", ["Don't", "Care"]],
             "stub_rsa": ELECTION_DUMMY_RSA_FERNET_FOUR
             },

            {"election_title": "Future Election 1",
             "description": "...",
             "start_date": (datetime.now(timezone.utc).astimezone() + timedelta(days=1)).isoformat(),
             "end_date": (datetime.now(timezone.utc).astimezone() + timedelta(days=2)).isoformat(),
             "creator_keys": ECDSAKeyPair(),
             "questions": ["Don't Care", ["Don't", "Care"]],
             "stub_rsa": ELECTION_DUMMY_RSA_FERNET_FIVE
             },

            {"election_title": "Future Election 2",
             "description": "...",
             "start_date": (datetime.now(timezone.utc).astimezone() + timedelta(days=1)).isoformat(),
             "end_date": (datetime.now(timezone.utc).astimezone() + timedelta(days=2)).isoformat(),
             "creator_keys": ECDSAKeyPair(),
             "questions": ["Don't Care", ["Don't", "Care"]],
             "stub_rsa": ELECTION_DUMMY_RSA_FERNET_SIX
             },
        ]

        self.session_manager.get_username = MagicMock(return_value=self.username)
        self.session_manager.election_creator_is_logged_in = MagicMock(return_value=True)
        self.session_manager.voter_is_logged_in = MagicMock(return_value=False)

        for election in elections:
            CryptoFlow.generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict = MagicMock(
                return_value=election['stub_rsa'])
            response = self.app.post("/api/election/create", headers=JSON_HEADERS,
                                     data=json.dumps(generate_election_post_data(**election)))
            assert response.data.decode('utf-8') == ELECTION_CREATED_SUCCESSFULLY.message
            assert response.status_code == ELECTION_CREATED_SUCCESSFULLY.code

    def test_can_retrieve_two_past_elections(self):
        response = self.app.get("/api/election/past", headers=JSON_HEADERS)
        past_elections = json.loads(response.data.decode('utf-8'))

        for election in past_elections:
            assert election["election_title"].startswith("Past")

    def test_can_retrieve_two_present_elections(self):
        response = self.app.get("/api/election/present", headers=JSON_HEADERS)
        present_elections = json.loads(response.data.decode('utf-8'))

        for election in present_elections:
            assert election["election_title"].startswith("Present")

    def test_can_retrieve_two_future_elections(self):
        response = self.app.get("/api/election/future", headers=JSON_HEADERS)
        future_elections = json.loads(response.data.decode('utf-8'))
        for election in future_elections:
            assert election["election_title"].startswith("Future")
