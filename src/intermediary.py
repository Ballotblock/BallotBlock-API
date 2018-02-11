#!/usr/bin/env python3
#
# src/server.py
# Authors:
#     Samuel Vargas

from flask import Flask

URL = "0.0.0.0"
DEBUG_URL = "127.0.0.1"
NAME = "BallotBlock Registration API"
PORT = 8080

app = Flask(__name__)

@app.route("/api/login/", methods=["GET", "POST"])
def login():
    """
    Creates a session_id that prevents the user from having to
    continually reauthenticate each time they make a
    subsequent request. The user should send this secret
    session id (essentially a cookie) each time they want
    to communicate with the intermediary server.
    :return:
    """
    raise NotImplementedError()

#
# Elections
#

@app.route("/api/election/create", methods=["GET", "POST"])
def election_create():
    """
    Allows an election creator (and an election creator only)
    to create a new election on the backend.

    If the election data is malformed, return an error.

    The election creator should send:

    ballot = {
        election = {
            "start_date": (unix_timestamp),
            "end_state": (unix_timestamp),
        },

        propositions = [
            {
                "question": "Favorite Letter?",
                "choices": ["A", "B", "C", "D"],
            },
            {
                "question": "Favorite Number?",
                "choices": ["1", "2", "3", "4"],
            },
            {
                ...
            }
        ]
    }

    Possible error types include:
        * Question without choices
        * Choices without questions
        * End_Date comes before Start_Date
        * Extremely short voting periods (eg 1 second)
    """
    raise NotImplementedError()

@app.route("/api/election/list", methods=["GET", "POST"])
def election_list():
    """
    Returns a list of elections that any user can
    participate in.
    """
    raise NotImplementedError()

@app.route("/api/election/<id>/join", methods=["GET", "POST"])
def election_join():
    """
    Allows the user to enter an election.
    """
    raise NotImplementedError()

@app.route("/api/election/<id>/schema", methods=["GET", "POST"])
def election_get_ballot_schema():
    """
    Returns a 'ballot' json object containing several propositions
    """
    raise NotImplementedError()


@app.route("/api/election/<id>/vote", methods=["GET", "POST"])
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
