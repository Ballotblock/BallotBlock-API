#!/usr/bin/env python3
#
# src/test/test_election_json_validator.py
# Authors:
#     Samuel Vargas

from src.validator.election_json_validator import ElectionJsonValidator
from src.validator import election_json_validator
import unittest
import time
import datetime


class TestElectionJsonValidator(unittest.TestCase):

    def test_valid_election(self):
        now = int(time.time())
        ten_days_later = int((datetime.datetime.fromtimestamp(now) + datetime.timedelta(days=10)).timestamp())

        election = {
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

        expected = election_json_validator.IS_VALID
        actual = ElectionJsonValidator().is_valid(election)
        assert actual == expected, "Expected: {0}, Got: {1}".format(expected, actual)

    def test_bad_start_date(self):
        raise NotImplementedError

    def test_bad_end_date(self):
        raise NotImplementedError
