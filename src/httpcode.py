#!/usr/bin/env python3
#
# src/httpcode.py
# Authors:
#     Samuel Vargas
#

from typing import NamedTuple
from collections import namedtuple
from flask_api import status

HttpCode = NamedTuple("httpcode", [("message", str), ("code", int)])

# General
SIGNUP_OK = \
    HttpCode("Signup successfully completed.", status.HTTP_201_CREATED)

LOGIN_SUCCESSFUL = \
    HttpCode("Login successful. You are now authenticated.", status.HTTP_200_OK)

# General
MISSING_OR_MALFORMED_JSON = \
    HttpCode("JSON was not provided or is non parseable", status.HTTP_400_BAD_REQUEST)

MISSING_LOGIN_PARAMETERS = \
    HttpCode("Missing 'username', 'password', or 'account_type'", status.HTTP_400_BAD_REQUEST)

USER_NOT_REGISTERED = \
    HttpCode("Register with the Registration server prior to signing-in", status.HTTP_400_BAD_REQUEST)

USER_ALREADY_AUTHENTICATED = \
    HttpCode("You have already logged in. Log out first before logging back in.", status.HTTP_400_BAD_REQUEST)

LOG_IN_FIRST = \
    HttpCode("You are not logged in. Login with /api/login/ first", status.HTTP_403_FORBIDDEN)

#
# Election Creation
#

ELECTION_WITH_TITLE_ALREADY_EXISTS = \
    HttpCode("You cannot create an election with this title because one already exists", status.HTTP_400_BAD_REQUEST)

ELECTION_MISSING_BALLOT_PUBLIC_KEY_OR_SIGNATURE = \
    HttpCode("This election is missing a ballot, public_key, or signature", status.HTTP_400_BAD_REQUEST)

ELECTION_BALLOT_MISSING_TITLE_DESCRIPTION_DATE_OR_QUESTIONS = \
    HttpCode("The election ballot is missing an election_title, description, start_date, end_date, or questions",
             status.HTTP_400_BAD_REQUEST)

ELECTION_BALLOT_SIGNING_MISMATCH = \
    HttpCode("The server could not verify that the ballot was signed using the public key based off the signature",
             status.HTTP_400_BAD_REQUEST)

ELECTION_BALLOT_JSON_MALFORMED = \
    HttpCode("Election json is malformed", status.HTTP_400_BAD_REQUEST)

ELECTION_CREATED_SUCCESSFULLY = \
    HttpCode("Election successfully created.", status.HTTP_201_CREATED)

VOTER_CANNOT_CREATE_ELECTION = \
    HttpCode("Voters are not allowed to create an election.", status.HTTP_400_BAD_REQUEST)

#
# Election Searching
#

ELECTION_SEARCH_BY_TITLE_MISSING_ELECTION_TITLE = \
    HttpCode("You forgot to specify the 'election_title' key", status.HTTP_400_BAD_REQUEST)

ELECTION_NOT_FOUND = \
    HttpCode("Couldn't find an election with this name.", status.HTTP_404_NOT_FOUND)

#
# Voting
#

ELECTION_VOTER_VOTED_ALREADY = \
    HttpCode("Voter has participated in this election already", status.HTTP_400_BAD_REQUEST)

ELECTION_VOTER_BALLOT_MISSING_TITLE_OR_ANSWERS = \
    HttpCode("Couldn't find 'election_title' or 'answers'", status.HTTP_400_BAD_REQUEST)

ELECTION_VOTER_BALLOT_MISSING_BALLOT_PUBLIC_KEY_OR_SIGNATURE = \
    HttpCode("Couldn't find 'ballot', 'voter_public_key', or 'ballot_signature'", status.HTTP_400_BAD_REQUEST)

ELECTION_VOTER_BALLOT_JSON_IS_MALFORMED = \
    HttpCode("Voter ballot json is malformed", status.HTTP_400_BAD_REQUEST)

ELECTION_VOTER_BALLOT_SIGNING_MISMATCH = \
    HttpCode("Could not verify that this voter ballot was signed using the provided signature, text, and publickey",
             status.HTTP_400_BAD_REQUEST)
