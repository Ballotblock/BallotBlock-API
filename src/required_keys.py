#!/usr/bin/env python3
#
# required_keys.py
# Authors:
#   Samuel Vargas

REQUIRED_LOGIN_KEYS = (
    "username",
    "password",
    "account_type"
)

#
# Elections
#

REQUIRED_ELECTION_MASTER_BALLOT_KEYS = (
    "election_title",
    "description",
    "start_date",
    "end_date",
    "questions"
)

REQUIRED_ELECTION_KEYS = (
    "master_ballot",
    "creator_public_key",
    "master_ballot_signature"
)

REQUIRED_ELECTION_SEARCH_BY_TITLE_KEYS = (
    "election_title",  # DO NOT remove this comma
)

REQUIRED_ELECTION_VOTE_BALLOT_KEYS = (
    "election_title",
    "answers"
)

REQUIRED_ELECTION_VOTE_KEYS = (
    "ballot",
    "voter_public_key",
    "ballot_signature"
)

#
# Tallying
#
REQUIRED_ELECTION_GET_ALL_BALLOTS_KEYS = (
    "election_title",
)

REQUIRED_ELECTION_TALLY_RESULTS_KEYS = (
    "election_title",
)

