#
# src/voter.py
# Authors:
#     Alex Gao
#


from src import user
import requests
from urllib.parse import quote
from flask import json

# Below is the url of the deployed hyperleder composer rest server
# for testing purposes, perhaps change url to locally deployed server
# as the state of the live server might be inconsistent
hyperledger = "http://13.57.203.209:3000/api/"

class voter(user.User):

    def __init__(self,voterId):
        self.voter = voterId

    def get_elections(self,electionId):
        """
        Returns all the details of an election given the electionID to identify the election
        Preforms a request to the hyperledger rest server to retrieve the json dump
        """
        electionId = quote(electionId)
        url = hyperledger + "elections/" + electionId
        result = requests.get(url)
        return result.json(), result.status_code

    def get_ballots(self):

        """
        Returns a list of all the ballots that a user holds
        example return json dump below:
        [
          {
            "$class": "org.hyperledger_composer.ballots.ballots",
            "ballotId": "Alice_ASASU2017 Election",
            "voter": "resource:org.hyperledger_composer.ballots.voters#Alice",
            "election": "resource:org.hyperledger_composer.ballots.elections#ASASU2017%20Election",
            "marked": false,
            "startDate": "2018-01-29T17:59:12.884Z",
            "endDate": "2018-03-29T17:59:12.884Z",
            "selections": [
              0
            ]
          }
        ]
        """
        resource = "resource:org.hyperledger_composer.ballots.voters#" + self.voter
        resource = quote(resource)
        url = hyperledger + "queries/getVoterBallots?voter=" + resource
        result = requests.get(url)
        return result.json(),result.status_code


