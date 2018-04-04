#!/usr/bin/env python3
#
# test/test_voting.py
# Authors:
#   Samuel Vargas
#

import unittest
from test.config import test_backend
from unittest.mock import MagicMock, patch
from test.test_util import generate_election_post_data, generate_voter_post_data, ELECTION_DUMMY_RSA_FERNET, \
    JSON_HEADERS
from src.crypto_suite import ECDSAKeyPair
from src.cookie_encryptor import CookieEncryptor
from src.validator.election_json_validator import ElectionJsonValidator
from src.crypto_flow import CryptoFlow
from src.time_manager import TimeManager
from src.account_types import AccountType
from src.httpcode import *
import json
import src.intermediary
import uuid


class VotingTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.election_title = "TestVoting"
        self.backend = test_backend()
        self.password = "Secret"
        self.app = src.intermediary.start_test(self.backend, self.password)
        CryptoFlow.generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict = MagicMock(
            return_value=ELECTION_DUMMY_RSA_FERNET)
        ElectionJsonValidator.is_valid = MagicMock(return_value=(True, ""))

    def setUp(self):
        # Delete all data prior to running the test
        self.backend.nuke()

        # Login as an Election Creator
        self.election_creator_auth_token = {
            'username': "ElectionCreator",
            'account_type': AccountType.election_creator.value,
            'authentication': CookieEncryptor(self.password).encrypt(b"ABC").decode('utf-8')
        }
        self.app.set_cookie('localhost', 'token', json.dumps(self.election_creator_auth_token))

        # Create an election
        self.election = generate_election_post_data(
            election_title=self.election_title,
            description="Test Voting Related Functionality",
            start_date=TimeManager.get_current_time_as_iso_format_string(),
            end_date=TimeManager.get_current_time_plus_time_delta_in_days_as_iso_8601_str(days=1),
            creator_keys=ECDSAKeyPair(),
            questions=["Red or Blue?", ["Red", "Blue"]],
        )
        response = self.app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(self.election))
        assert response.data.decode("utf-8") == ELECTION_CREATED_SUCCESSFULLY.message

        # Login as a voter
        self.voter_auth_token = {
            'username': "Voter",
            'account_type': AccountType.voter.value,
            'authentication': CookieEncryptor(self.password).encrypt(b"ABC").decode('utf-8')
        }

        self.app.set_cookie('localhost', 'token', json.dumps(self.voter_auth_token))

        # Cast a single vote as a voter
        self.voter_ecdsa_keys = ECDSAKeyPair()
        self.ballot = generate_voter_post_data(
            election_title=self.election_title,
            voter_keys=self.voter_ecdsa_keys,
            answers=["Red"]
        )

        # Verify that the vote was cast
        response = self.app.post("/api/election/vote", headers=JSON_HEADERS, data=json.dumps(self.ballot))
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
        data = json.dumps({'voter_uuid': self.voter_uuid})
        response = self.app.post("/api/ballot/get", headers=JSON_HEADERS, data=data)
        ballot_signature = json.loads(response.data)['ballot_signature']
        assert self.voter_ecdsa_keys.is_signed(ballot_signature.encode('utf-8'), self.ballot['ballot'].encode('utf-8'))

    def test_voter_cannot_see_decrypted_ballot_during_election(self):
        data = json.dumps({'voter_uuid': self.voter_uuid})
        response = self.app.post("/api/ballot/get", headers=JSON_HEADERS, data=data)
        retrieved_ballot = json.loads(response.data)
        assert retrieved_ballot['ballot'] != self.ballot['ballot']

    @patch("src.time_manager.TimeManager")
    def test_voter_can_retrieve_decrypted_ballot_when_election_is_over(self, mock):
        mock.return_value = False
        data = json.dumps({'voter_uuid': self.voter_uuid})
        response = self.app.post("/api/ballot/get", headers=JSON_HEADERS, data=data)
        retrieved_ballot = json.loads(response.data)
        assert retrieved_ballot['ballot'] == self.ballot['ballot']
