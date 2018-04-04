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
from test.test_util import generate_election_post_data, ELECTION_DUMMY_RSA_FERNET, JSON_HEADERS
from src.httpcode import *
from src.crypto_suite import ECDSAKeyPair
from src.crypto_flow import CryptoFlow
from src.validator import ElectionJsonValidator
from src.time_manager import TimeManager
from src.account_types import AccountType
from src.cookie_encryptor import CookieEncryptor
from unittest.mock import MagicMock, patch


class ElectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Election Data
        self.username = "ElectionCreator"
        self.election_title = "ElectionTest"
        self.election_description = "Election Creation, Retrieval, Encryption, Decryption"
        self.start_date = TimeManager.get_current_time_as_iso_format_string()
        self.end_date = TimeManager.get_current_time_plus_time_delta_in_days_as_iso_8601_str(days=1)
        self.election_creator_ecdsa_keys = ECDSAKeyPair()
        self.questions = ["A or B?", ["A", "B"]]
        self.election = generate_election_post_data(
            election_title=self.election_title,
            description=self.election_description,
            start_date=self.start_date,
            end_date=self.end_date,
            creator_keys=self.election_creator_ecdsa_keys,
            questions=self.questions)

        # Test Data
        self.password = "Secret"
        self.backend = test_backend()
        self.app = src.intermediary.start_test(self.backend, self.password)

        # Setup Authentication Cookie
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
        # Reset the backend and create a new election each test.
        self.backend.nuke()
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

    @patch("src.time_manager.TimeManager.election_in_progress")
    def test_election_private_key_is_leaked_after_election(self, mock):
        mock.return_value = False
        search = json.dumps({"election_title": self.election_title})
        response = self.app.get("/api/election/get_by_title", headers=JSON_HEADERS, data=search)
        assert response.status_code == 200
        retrieved_election = json.loads(response.data.decode('utf-8'))
        assert 'election_private_key' in retrieved_election
