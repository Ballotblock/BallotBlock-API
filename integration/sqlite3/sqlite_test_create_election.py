#!/usr/bin/env python3
#
# integration/sqlite3/sqlite_test_create_election.py
# Authors:
#   Samuel Vargas
#

from unittest.mock import MagicMock
from src import httpcode
import json
import uuid
import unittest
import time
import datetime
import src.intermediary

JSON_HEADERS = {"Content-Type": "application/json"}


class CreateElectionTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.app = src.intermediary.start_test_sqlite(":memory:")

        self.election_creator = {
            "username": "Sam",
            "password": "123456",
            "account_type": "election_creator"
        }

        now = int(time.time())
        ten_days_later = int((datetime.datetime.fromtimestamp(now) + datetime.timedelta(days=10)).timestamp())

        self.election_data = {
            "username": "Sam",
            "start_date": now,
            "end_date": ten_days_later,
            "title": "Color Shape Election",
            "description": "This is a test election about favorite color / shape.",
            "propositions": [
                {
                    "question": "What is your favorite color?",
                    "choices": ["Red", "Green", "Blue", "Yellow"],
                },
                {
                    "question": "What is your favorite shape?",
                    "choices": ["Triangle", "Square", "Circle", "Diamond"],
                }
            ]
        }

        self.sessionID = uuid.uuid4()

    def test_user_can_create_election(self):
        # Assume the user is registered.
        src.intermediary.REGISTRATION_PROVIDER.is_user_registered = MagicMock(return_value=True)

        # Assume the user election data is always valid for now.
        src.intermediary.ELECTION_JSON_VALIDATOR.is_valid = MagicMock(
            return_value=(True, "Testing, data is assumed to be valid."))

        # Log the election creator in
        response = self.app.post("/api/login",
                                 headers=JSON_HEADERS,
                                 data=json.dumps(self.election_creator))

        expectedCode = httpcode.LOGIN_SUCCESSFUL.code
        expectedMessage = httpcode.LOGIN_SUCCESSFUL.message
        actualCode = response.status_code
        actualMessage = response.data.decode("utf-8")
        assert expectedCode == actualCode and actualMessage == expectedMessage, \
            "Login should have been successful but failed."

        # Verify we're now authenticated with the intermediary server
        response = self.app.post("/api/login",
                                 headers=JSON_HEADERS,
                                 data=json.dumps(self.election_creator))
        expectedCode = httpcode.USER_ALREADY_AUTHENTICATED.code
        expectedMessage = httpcode.USER_ALREADY_AUTHENTICATED.message
        actualCode = response.status_code
        actualMessage = response.data.decode("utf-8")
        assert expectedCode == actualCode and actualMessage == expectedMessage, \
            "Intermediary server should see our previous login."

        # Send a request to create an election
        response = self.app.post("/api/election/create",
                                 headers=JSON_HEADERS,
                                 data=json.dumps(self.election_data))

        # TODO:
        # * Implement election_create()
        # * Implement election

        # 4) Verify that when we query the server with our username
        # 5) We recieve

        # Tasks to complete for this integration test:
        # 1) Send request to server to create an election with user_a
        # 2) user_b joins the election, receives a set of public private keys
        # 3) user_b downloads a ballot schema for this particular election
        # 4) user_b fills out the ballot schema with their voting choices
        # 5) user_b casts their ballot cementing it in the voting ledger / db
        # 6) user_b redownloads the blockchain / db and manually verifies that their
        #    encrypted ballot was included.
