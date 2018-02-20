
#!/usr/bin/env python3
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
from src.voter import Voter
from src.sqlite3 import SQLiteElectionProvider
from src.sessions import MemorySessionProvider
from src.registration import RegistrationServerProvider

URL = "0.0.0.0"
DEBUG_URL = "127.0.0.1"
NAME = "BallotBlock API"
PORT = 8080
BACKEND_TYPE = None

# Miscellaneous providers
ELECTION_PROVIDER = None
SESSION_PROVIDER = MemorySessionProvider()
REGISTRATION_PROVIDER = RegistrationServerProvider()



def start_test_sqlite(db_path: str):
    ELECTION_PROVIDER = SQLiteElectionProvider(db_path)
    BACKEND_TYPE = BackendType['SQLite']
    test_app = app.test_client()
    test_app.testing = True
    return test_app


@app.route("/")
def index():
    return("Ballotblock API")



#
# Elections
#



@app.route("/api/election/list", methods=["GET", "POST"])
def election_list():
    """
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


@app.route("/api/election/<id>/get", methods=["GET", "POST"])
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

