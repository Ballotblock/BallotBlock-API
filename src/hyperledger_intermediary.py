from flask import Flask, request, jsonify, session
from src import httpcode
from src.validator import ElectionJsonValidator
from src.time_manager import TimeManager
from src import app
from src.hyperledger.hyperledger_backend_io import HyperledgerBackendIO


ELECTION_JSON_VALIDATOR = ElectionJsonValidator()
TIME_MANAGER = TimeManager()

#change the url below is needed
BACKEND = HyperledgerBackendIO("http://35.197.34.20:3000/api/")

@app.route("/api/election/", methods=["POST"])
def create_election():
    """
    Allows an election creator to create a new election on the backend.

    accepts the following json schema:

   {
        "electionTitle": "Election1",
        "propositions": [{ 
        		"question" : "question1",
                "choices" : ["c1", "c2" ],
                "id" : "Election1question1"
        	}],
          "startDate" : "2018-04-29T17:59:12.884Z" , 
         "endDate" : "2018-04-29T17:59:12.884Z"   
    }
    """
    userId = request.args.get('id')
    creator = userId;
    content = request.get_json(silent=True, force=True);

    electionTitle = content['electionTitle']
    propositions = content['propositions']
    startDate  = content['startDate']
    endDate = content['endDate']
    json = BACKEND.create_election(creator,electionTitle,propositions,startDate,endDate)
    return jsonify(json)

@app.route("/api/election/current", methods=["GET"])
def current_election_list():
    """
    Returns a list of all the current elections
    """
    json = BACKEND.get_current_elections()
    response = jsonify(json)
    return response

@app.route("/api/election/past", methods=["GET"])
def past_election_list():
    """
    Returns a list of all the current elections
    """

    json = BACKEND.get_past_elections()
    response = jsonify(json)
    return response

@app.route("/api/election/upcomming", methods=["GET"])
def upcomming_election_list():
    """
    Returns a list of all the current elections
    """
    json = BACKEND.get_upcomming_elections()
    response = jsonify(json)
    return response


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

    accepts a post request in the following format
    {
        "election" : "some election"
        "answers" : [1,2,3,4]
    }
    """
    content = request.get_json(silent=True, force=True)
    userId = request.args.get('id')
    json = BACKEND.create_ballot(userId,content['election'],content['answers'])
    return jsonify(json)

@app.route("/api/election/<id>", methods=["GET"])
def election_get(id):
    electionId = id
    userId = request.args.get('id')
    json = BACKEND.get_election_by_title(userId,electionId)
    response = jsonify(json)
    return response
