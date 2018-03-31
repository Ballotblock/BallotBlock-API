#!/usr/bin/env python3
#
# test/test_election.py
# Authors:
#   Samuel Vargas
#

import json
import unittest
import src.intermediary
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

JSON_HEADERS = {"Content-Type": "application/json"}


class ElectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.registration_provider = RegistrationServerProvider()
        self.election_json_validator = ElectionJsonValidator()
        self.session_manager = SessionManager()
        self.time_manager = TimeManager()
        self.election_json_validator.is_valid = MagicMock(return_value=(True, ""))
        self.registration_provider.is_user_registered = MagicMock(return_value=True)
        self.session_manager.is_logged_in = MagicMock(return_value=True)

        # Election Data
        self.election_creator_ecdsa_keys = ECDSAKeyPair()
        self.username = "ElectionCreator"
        self.election_title = "ElectionTest"
        self.election_description = """
            This test verifies that:
            1) The user can create an election
            2) The user can retrieve that election and all the details are unencrypted
               / the same.
            3) If the user retrieves the election PRIOR to the election conclusion
               then the private key is not leaked.
            4) If the user retrieves the election after the election conclusion
        """

        self.start_date = TimeManager.get_current_time_as_iso_format_string()
        self.end_date = TimeManager.get_current_time_plus_time_delta_in_days_as_iso_8601_str(days=1)


    def setUp(self):
        CryptoFlow.generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict = MagicMock(
            return_value=ELECTION_DUMMY_RSA_FERNET)

        # Setup an election
        self.app = src.intermediary.start_test_sqlite(
            backend_io=SQLiteBackendIO(":memory:"),
            session_manager=self.session_manager,
            election_json_validator=self.election_json_validator,
            registration_provider=self.registration_provider,
            time_manager=self.time_manager
        )

        self.election = generate_election_post_data(
            election_title=self.election_title,
            description=self.election_description,
            start_date=self.start_date,
            end_date=self.end_date,
            creator_keys=self.election_creator_ecdsa_keys,
            questions=["Red or Blue?", ["Red", "Blue"]])

        self.session_manager.get_username = MagicMock(return_value=self.username)
        self.session_manager.election_creator_is_logged_in = MagicMock(return_value=True)
        self.session_manager.voter_is_logged_in = MagicMock(return_value=False)
        response = self.app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(self.election))
        assert response.data.decode('utf-8') == ELECTION_CREATED_SUCCESSFULLY.message
        assert response.status_code == ELECTION_CREATED_SUCCESSFULLY.code

    def test_election_creator_can_retrieve_correct_election_data(self):
        search = json.dumps({"election_title": self.election_title})
        response = self.app.get("/api/election/get_by_title", headers=JSON_HEADERS, data=search)
        assert response.status_code == 200
        retrieved_election = json.loads(response.data.decode('utf-8'))

        assert retrieved_election['creator_username'] == self.username
        assert retrieved_election['creator_public_key'] == self.election_creator_ecdsa_keys \
            .get_public_key_b64().decode('utf-8')
        assert retrieved_election['description'] == self.election_description
        assert retrieved_election['election_title'] == self.election_title
        assert retrieved_election['start_date'] == self.start_date
        assert retrieved_election['end_date'] == self.end_date
        master_ballot = json.loads(self.election['master_ballot'])
        questions_str = json.dumps(master_ballot['questions'])
        assert retrieved_election['questions'] == questions_str

    def test_election_private_key_is_not_leaked_during_election(self):
        assert self.start_date < self.end_date
        search = json.dumps({"election_title": self.election_title})
        response = self.app.get("/api/election/get_by_title", headers=JSON_HEADERS, data=search)
        assert response.status_code == 200
        retrieved_election = json.loads(response.data.decode('utf-8'))
        assert 'election_private_key' not in retrieved_election

    def test_election_private_key_is_leaked_after_election(self):
        fn = self.time_manager.election_in_progress
        self.time_manager.election_in_progress = MagicMock(return_value=False)
        search = json.dumps({"election_title": self.election_title})
        response = self.app.get("/api/election/get_by_title", headers=JSON_HEADERS, data=search)
        self.time_manager.election_in_progress = fn
        assert response.status_code == 200
        retrieved_election = json.loads(response.data.decode('utf-8'))
        assert 'election_private_key' in retrieved_election
