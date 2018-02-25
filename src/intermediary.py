# !/usr/bin/env python3
#
# Path modification trick to allow you to execute the program
# using either:
#     * python -m src.intermediary
#     * python intermediary.py

import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

# Subdirectories
SUBDIRECTORIES = [
    "..",
    "interfaces",
    "sqlite3",
]

for subdirectory in SUBDIRECTORIES:
    sys.path.append(os.path.join(dir_path, subdirectory))

#
# src/intermediary.py
# Authors:
#     Samuel Vargas
#     Alex Gao

from flask import Flask, request, jsonify
from src import app
from src.backend_type import BackendType
from src import httpcode
from src.validator import ElectionJsonValidator
from src.voter import Voter
from src.sessions import MemorySessionProvider
from src.registration import RegistrationServerProvider
from src.sqlite3 import SQLiteElectionProvider
#from src.sqlite3 i#mport BackendInitializer

URL = "0.0.0.0"
DEBUG_URL = "127.0.0.1"
NAME = "BallotBlock API"
PORT = 8080
BACKEND_TYPE = None

# Miscellaneous providers
ELECTION_PROVIDER = None
SESSION_PROVIDER = MemorySessionProvider()
REGISTRATION_PROVIDER = RegistrationServerProvider()
BACKEND_INITIALIZER = None


def start_test_sqlite(db_path: str):
    ELECTION_PROVIDER = SQLiteElectionProvider(db_path)
    BACKEND_INITIALIZER = None
    BACKEND_TYPE = BackendType['SQLite']
    test_app = app.test_client()
    test_app.testing = True
    return test_app


@app.route("/")
def index():
    return ("BallotBlock API")


@app.route("/api/login", methods=["GET", "POST"])
def login() -> httpcode.HttpCode:
    # JSON is missing or malformed
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # At least one required parameter is missing
    required_keys = ("username", "password", "account_type")
    key_is_missing = all(key not in content.keys() for key in required_keys)
    if key_is_missing:
        return httpcode.MISSING_LOGIN_PARAMETERS

    # The registration server says this user is invalid:
    if not REGISTRATION_PROVIDER.is_user_registered(content['username'], content['password']):
        return httpcode.USER_NOT_REGISTERED

    # The user is already authenticated
    if SESSION_PROVIDER.is_authenticated(content['username']):
        return httpcode.USER_ALREADY_AUTHENTICATED

    # All tests passed, authenticate the user.
    SESSION_PROVIDER.authenticate_user(content['username'])
    return httpcode.LOGIN_SUCCESSFUL


#
# Elections
#

@app.route("/api/election", methods=["POST"])
def election_create() -> httpcode.HttpCode:
    """
    
    "create" part at the end of the route removed to follow REST standard.
    POST now implies that you are creating the resource "election"
    
    Allows an election creator (and an election creator only)
    to create a new election on the backend.
    If the election data is malformed, return an error.
    The election creator should send the following in
    JSON format:
    Election should double check that the user
    has permission to create an election.
    election = {
        "username": "user creating the election"
        "start_date": unix timestamp,
        "end_date": unix timestamp,
        "title": "2016 U.S. Presidential Election",
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
    Possible error types include:
        * Question without choices
        * Choices without questions
        * End_Date comes before Start_Date
        * Extremely short voting periods (eg 1 second)
    """

    # Check if any JSON was supplied at all
    content = request.get_json(silent=True, force=True)
    if content is None:
        return httpcode.MISSING_OR_MALFORMED_JSON

    # Verify the user has logged in first
    if not SESSION_PROVIDER.is_authenticated(content['username']):
        return httpcode.LOG_IN_FIRST

    # User is an election creator
    raise NotImplementedError()

    # Ensure election JSON is valid
    validator = ElectionJsonValidator(content)
    if not validator.isValid():
        return validator.reason(), 400

    # Ensure election with this title does not already exist.
    raise NotImplementedError()

    return httpcode.ELECTION_CREATED_SUCCESSFULLY


@app.route("/api/election/", methods=["GET"])
def election_list():
    """
    
    "list" part in the route removed, GET request means
    you are going to get a list of all the elections associated with the user.
    
    Returns a list of elections that any user can
    participate in.
    A user can participate in an election if that user
    holds a ballot for that election.
    Here this method will return a list of ballots that a user currently holds
    Example of an api call
    http://127.0.0.1:5000/api/election/list?id=someId
    Note that this initial implementation is likely change as
    the login route above is implemented. Instead we would
    extract the id from the token created by logging in first
    """
    id = request.args.get('id')
    user = voter(id)
    json = user.get_ballots()
    return jsonify(json), 200


@app.route("/api/election/<id>", methods=["GET"])
def election_get(id):
    """
    Gets all the details of the elections:
        start date, end date, propositions, title
    So the front end can fill in the interface components
    Example of an api call:
    http://127.0.0.1:5000/api/election/id/get?id=someId
    One that should work for and return some json data:
    http://127.0.0.1:5000/api/election/ASASU2017 Election/get?id=Alice
    Note that this initial implementation is likely change as
    the login route above is implemented. Instead we would
    extract the id from the token created by logging in first
    The token would be passed in the request in perhaps bearer or cookie
    """
    electionId = id;
    userId = request.args.get('id')
    user = voter(userId)
    json = user.get_elections(electionId)
    return jsonify(json), 200


@app.route("/api/ballot", methods=["POST"])
def election_join():
    """
    Allows the user to enter an election.
    When the user creates a ballot by doing a post request, a user can
    then participate in the election
    """
    raise NotImplementedError()


@app.route("/api/ballot", methods=["GET"])
def election_get_ballot_schema():
    """
    Returns a 'ballot' json object containing several propositions
    """
    raise NotImplementedError()


@app.route("/api/vote", methods=["POST"])
def election_vote():
    """
    Allows the user to cast a vote (sending the contents
    of their filled out ballot.
    If their ballot is missing or contains invalid data return
    an error. Otherwise accept their ballot and store it
    on the backend.
    Users may only cast their vote ONCE. Election creators
    may not cast votes. Only create elections.
    """
    raise NotImplementedError()
