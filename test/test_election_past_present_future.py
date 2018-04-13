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
from src.validator import ElectionJsonValidator
from src.time_manager import TimeManager
from src.account_types import AccountType
from src.cookie_encryptor import CookieEncryptor
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

JSON_HEADERS = {"Content-Type": "application/json"}


class ElectionPastPresentFutureTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Setup Authentication Cookie
        self.password = "Secret"
        self.backend = test_backend()
        self.app = src.intermediary.start_test(self.backend, self.password)

        self.auth_token = {
            'username': 'ElectionCreator',
            'account_type': AccountType.election_creator.value,
            'authentication': CookieEncryptor(self.password).encrypt(b"ABC").decode('utf-8')
        }

        self.app.set_cookie('localhost', 'token', json.dumps(self.auth_token))

        # Mocks
        ElectionJsonValidator.is_valid = MagicMock(return_value=(True, ""))
        CryptoFlow.generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict = MagicMock(
            return_value=ELECTION_DUMMY_RSA_FERNET)

    def setUp(self):
        # Delete all data prior to running the test
        self.backend.nuke()

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

        for election in elections:
            # Stub the RSA Fernet Key with a unique one each time.
            CryptoFlow.generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict = MagicMock(
                return_value=election['stub_rsa'])

            # Create the election
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
