#!/usr/bin/env python3
#
# test/test_intermediary.py
# Authors:
#   Samuel Vargas
#

# This test is responsible for ensuring that the API works correctly.
# A new SQLite3 memory database is used for each test but the tests should
# pass for any backend.

import json
import uuid
import unittest
import datetime
import time
import src.intermediary
from src.httpcode import *
from src.ecdsa_keypair import ECDSAKeyPair
from src.sqlite import SQLiteBackendIO
from src.validator import ElectionJsonValidator
from src.registration import RegistrationServerProvider
from unittest.mock import MagicMock
from typing import List, Callable

JSON_HEADERS = {"Content-Type": "application/json"}


def generate_election(election_title: str = None,
                      description: str = None,
                      start_date: int = int(time.time()),
                      end_date: int = int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()),
                      creator_keys: ECDSAKeyPair = None,
                      questions: List[List] = None):
    if not election_title:
        election_title = str(uuid.uuid4())

    if not description:
        description = str(uuid.uuid4())

    assert creator_keys and questions

    master_ballot_json_str = json.dumps({
        "election_title": election_title,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "questions": questions,
    })

    return {
        "master_ballot": master_ballot_json_str,
        "creator_public_key": creator_keys.get_public_key_hex_str(),
        "master_ballot_signature": creator_keys.sign_with_private_key_and_retrieve_hex_signature(master_ballot_json_str)
    }


def fake_authentication_and_run_callback(app, username: str, account_type: str, callback: Callable):
    with app as c:
        with c.session_transaction() as sess:
            sess['username'] = username
            sess['account_type'] = account_type
        callback()


def get_test_client_without_registration_or_validation_and_empty_db(db_path=":memory:"):
    registration_provider = RegistrationServerProvider()
    election_json_validator = ElectionJsonValidator()
    election_json_validator.is_valid = MagicMock(return_value=(True, ""))
    registration_provider.is_user_registered = MagicMock(return_value=True)
    return src.intermediary.start_test_sqlite(
        backend_io=SQLiteBackendIO(db_path),
        election_json_validator=election_json_validator,
        registration_provider=registration_provider
    )


class IntermediaryTest(unittest.TestCase):
    # Election Creation
    def test_election_creator_can_create_single_election(self):
        app = get_test_client_without_registration_or_validation_and_empty_db()
        username = "Samulus"
        account_type = "ElectionCreator"

        def test():
            election = generate_election(questions=[["A or B", ["A, B"]]], creator_keys=ECDSAKeyPair())
            response = app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(election))
            assert response.data.decode('utf-8') == ELECTION_CREATED_SUCCESSFULLY.message
            assert response.status_code == ELECTION_CREATED_SUCCESSFULLY.code

        fake_authentication_and_run_callback(app, username, account_type, test)

    def test_election_creator_can_create_multiple_elections(self):
        app = get_test_client_without_registration_or_validation_and_empty_db("/home/sam/SOPHIE.db")
        username = "Samulus"
        account_type = "ElectionCreator"
        number_of_elections = 3
        elections = []

        def test():
            for _ in range(number_of_elections):
                elections.append(generate_election(questions=[["A or B", ["A, B"]]], creator_keys=ECDSAKeyPair()))
                response = app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(elections[-1]))
                assert response.data.decode('utf-8') == ELECTION_CREATED_SUCCESSFULLY.message
                assert response.status_code == ELECTION_CREATED_SUCCESSFULLY.code

        fake_authentication_and_run_callback(app, username, account_type, test)

    #
    # Election Retrieval / Search
    #

    def test_election_creator_data_is_stored_correctly(self):
        app = get_test_client_without_registration_or_validation_and_empty_db()
        username = "Samulus"
        account_type = "ElectionCreator"

        def test():
            election = generate_election(questions=[["A or B", ["A, B"]]], creator_keys=ECDSAKeyPair())
            response = app.post("/api/election/create", headers=JSON_HEADERS, data=json.dumps(election))
            assert response.data.decode('utf-8') == ELECTION_CREATED_SUCCESSFULLY.message
            assert response.status_code == ELECTION_CREATED_SUCCESSFULLY.code

        fake_authentication_and_run_callback(app, username, account_type, test)