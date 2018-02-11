#!/usr/bin/env python3
#
# src/interface/server.py
# Authors:
#     Samuel Vargas
#     Alex Gao

from flask import Flask,request,jsonify,make_response
from src.voter import  voter

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
    return  jsonify(json),200

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
    return jsonify(json),200

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


app.run()