#!/usr/bin/env python3
#
# integration/sqlite3/sqlite_test_create_election.py
# Authors:
#   Samuel Vargas
#

from unittest.mock import MagicMock
import json
import unittest
import src.intermediary
import time
import datetime
from src.httpcode import ELECTION_CREATED_SUCCESSFULLY
from src.key import generate_edsca_keypair
from src.validator import ElectionJsonValidator
from src.registration import RegistrationServerProvider
from src.sqlite import SQLiteBackendIO
from src.key import is_data_signed_with_public_key

JSON_HEADERS = {"Content-Type": "application/json"}
PRESERVE_CONTEXT_ON_EXCEPTION = False


class CreateElectionTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # Setup server with correct objects
        backend_io = SQLiteBackendIO(":memory:")
        registration_provider = RegistrationServerProvider()
        election_json_validator = ElectionJsonValidator()

        election_json_validator.is_valid = MagicMock(return_value=(True, "JSON is ok"))
        registration_provider.is_user_registered = MagicMock(return_value=True)

        self.app = src.intermediary.start_test_sqlite(
            backend_io=backend_io,
            election_json_validator=election_json_validator,
            registration_provider=registration_provider
        )

        keys = generate_edsca_keypair()

        start_date = int(time.time())
        end_date = int((datetime.datetime.fromtimestamp(start_date) + datetime.timedelta(days=1)).timestamp())

        self.master_ballot_json_str = json.dumps({
            "election_title": "The Favorite Color and Shape Election",
            "description": "This is an election about your favorite color and shape.",
            "start_date": start_date,
            "end_date": end_date,
            "questions": [["Favorite Color?", ["Red", "Blue"]],
                          ["Favorite Shape?", ["Square", "Triangle"]]]
        })

        self.election_post = {
            "master_ballot": self.master_ballot_json_str,
            "creator_public_key": str(keys.public.to_string().hex()),
            "master_ballot_signature": str(keys.private.sign(self.master_ballot_json_str.encode('utf-8')).hex())
        }

        # Session management information
        self.username = "Samulus"
        self.account_type = "ElectionType"

    def test_a_election_creator_can_create_election(self):
        with self.app as c:
            # Mock out logging into the API
            with c.session_transaction() as sess:
                sess['username'] = self.username
                sess['account_type'] = self.account_type

            response = self.app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(self.election_post))

            assert response.data.decode('utf-8') == ELECTION_CREATED_SUCCESSFULLY.message
            assert response.status_code == ELECTION_CREATED_SUCCESSFULLY.code

    def test_b_election_creator_can_retrieve_and_verify_their_election(self):
        with self.app as c:
            # Mock out logging into the API
            with c.session_transaction() as sess:
                sess['username'] = self.username
                sess['account_type'] = self.account_type

            # Send get request to server
            master_ballot_dict = json.loads(self.master_ballot_json_str)
            data = {"election_title": master_ballot_dict["election_title"]}

            response = self.app.get("/api/election/get_by_title", headers=JSON_HEADERS, data=json.dumps(data))
            assert response.status_code == 200
            retrieved_election = json.loads(response.data)

            # Verify that the server didn't leak the 'election_private_key' as the election
            # hasn't ended yet. (It ends in 1 day)
            assert 'election_private_key' not in retrieved_election

            # Verify that the election data used to create the election is identical
            # to the data that was retrieved.
            assert retrieved_election["election_title"] == master_ballot_dict["election_title"]
            assert retrieved_election["description"] == master_ballot_dict["description"]
            assert retrieved_election["start_date"] == master_ballot_dict["start_date"]
            assert retrieved_election["end_date"] == master_ballot_dict["end_date"]
            assert json.loads(retrieved_election["questions"]) == master_ballot_dict["questions"]
            assert retrieved_election["creator_username"] == self.username
            assert retrieved_election["creator_public_key"] == self.election_post["creator_public_key"]
            assert retrieved_election["master_ballot_signature"] == self.election_post["master_ballot_signature"]

            # Verify that the server did not tamper with our data by validating our signature
            assert is_data_signed_with_public_key(retrieved_election["creator_public_key"],
                                                  retrieved_election["master_ballot_signature"],
                                                  self.master_ballot_json_str)
