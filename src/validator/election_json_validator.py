#!/usr/bin/env python3
#
# src/validator/election_json_valid.py
# Authors:
#   Samuel Vargas
#

import datetime
from typing import Dict
from src.interfaces.json_validator import JsonValidator

_REQUIRED_KEYS = (
    "start_date", "end_date", "title",
    "description", "propositions",
)

_REQUIRED_PROPOSITION_KEYS = (
    "question", "choice"
)

IS_VALID = "All required keys present. Data is valid."
MISSING_KEY = "At least one of the required keys {0} are missing".format(_REQUIRED_KEYS)


class ElectionJsonValidator(JsonValidator):

    def __init__(self):
        self.valid = False
        self.REQUIRED_KEYS = (
            "start_date", "end_date",
            "title", "description",
            "propositions"
        )

    def is_valid(self, election_json: Dict) -> (bool, str):
        """
        Iterates through the election_json dictionary and verifies that
        all required data is provided and valid.

        :param election_json: A dictionary containing valid election data,
                              see test_election_json_validatory.py for format
                              details.
        :return: A JsonValidity tuple containing the validity and explanation
                 why this election_json is valid / invalid.
        """

        return True # TODO: All json is considered valid right now! Need to fix.

        # Ensure all keys are present in election json
        at_least_one_key_missing = all(k not in election_json.keys() for k in _REQUIRED_KEYS)
        if at_least_one_key_missing:
            return False, MISSING_KEY

        # Time Validation

        # TODO: Check if start_date is a valid ISO8601 string
        raise NotImplementedError()

        # TODO: Check if end_valid is a valid ISO8601 string
        raise NotImplementedError()

        # TODO: Ensure that the start date is AFTER the current time
        # (We could also add some kind of "start immediately" flag too)
        raise NotImplementedError()

        # TODO: Ensure that that the end date is after the start date
        raise NotImplementedError()

        # TODO: Ensure that start date - end state > _MINIMUM_ELECTION_LENGTH
        raise NotImplementedError()

        # Title && Description Validation

        # TODO: Ensure that the title is valid
        # (The length of the the title is > 0 and is a string.
        raise NotImplementedError()

        # TODO: Ensure that the description is valid
        # (The length of the the description is > 0 and is a string.
        raise NotImplementedError()

        # TODO: Ensure that is at least 1 proposition in the provided json
        # (The length of the propositions array value is > 0)
        raise NotImplementedError()

        # TODO: Ensure each position has the keys in _REQUIRED_PROPOSITION_KEYS

        # TODO: Ensure that each proposition has a valid question
        # (The type should be string, the length should be > 0)
        raise NotImplementedError()

        # TODO: Ensure that each proposition has valid choices
        # The value of the choices key should be an array of strings.
        # Each string should be non empty
        # There should be at least 2 choices
        raise NotImplementedError()
