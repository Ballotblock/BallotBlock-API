#!/usr/bin/env python3
#
# integration/test_create_election.py
# Authors:
#   Samuel Vargas
#

import unittest
import time
import datetime


class CreateElectionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        user_a = {
            "username": "Sam",
            "password": "123456",
            "account_type": "election_creator"
        }

        user_b = {
            "username": "Paul",
            "password": "hunter2",
            "account_type": "voter"
        }


        now = int(time.time())
        ten_days_later = int((datetime.datetime.fromtimestamp(now) + datetime.timedelta(days=28)).timestamp())

        election = {
            "start_date": now,
            "end_date": ten_days_later
        }

        propositions = [
            {
            "question": "What is your favorite color?",
            "choices":  ["Red", "Green", "Blue", "Yellow"],
            },
            {
            "question": "What is your favorite shape?",
            "choices":  ["Triangle", "Square", "Circle", "Diamond"],
            }
        ]

        # Tasks to complete for this integration test:
        # 1) Send request to server to create an election with user_a
        # 2) user_b joins the election, receives a set of public private keys
        # 3) user_b downloads a ballot schema for this particular election
        # 4) user_b fills out the ballot schema with their voting choices
        # 5) user_b casts their ballot cementing it in the voting ledger / db
        # 6) user_b redownloads the blockchain / db and manually verifies that their
        #    encrypted ballot was included.
