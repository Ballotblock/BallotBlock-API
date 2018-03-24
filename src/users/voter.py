#
# src/users/voter.py
# Authors:
#     Alex Gao
#

import requests
from urllib.parse import quote
from flask import json
from .filter import Filter

# Below is the url of the deployed hyperleder composer rest server
# for testing purposes, perhaps change url to locally deployed server
# as the state of the live server might be inconsistent
hyperledger = "http://13.57.203.209:3000/api/"

class Voter():

    def __init__(self,voterId):
        self.voter = voterId

    def get_election(self,electionId):
        """
        Returns all the details of an election given the electionID to identify the election
        Also preforms a request to see if the user holds a ballot for that specific election
        If there is a ballot, return the selections
        Preforms a request to the hyperledger rest server to retrieve the json dump
        """
        
        url = hyperledger + "elections/" + electionId
        result = requests.get(url)

        ballotId = self.voter +"_" + electionId;
        url2 = hyperledger + "ballots/" + ballotId + "?filter=" + Filter.ballot_filter();
        result2 = requests.get(url2);

        if(result2.status_code == 200):
            response = {
                "election":result.json(),
                "ballot":result2.json()
                }
        else:
            response = {
                "election":result.json(),
                "ballot": False
                }
        return response, result.status_code

    def get_current_elections(self):
        """
        Returns only the electionId(s) of current elections
        """

        url = hyperledger + "elections?filter="  + Filter.current_filter();
        result = requests.get(url)
        return result.json(), result.status_code

    def get_past_elections(self):
        """
        Returns only the electionId(s) of current elections
        """

        url = hyperledger + "elections?filter="  + Filter.past_filter();
        result = requests.get(url)
        return result.json(), result.status_code


    def get_upcomming_elections(self):
        """
        Returns only the electionId(s) of current elections
        """

        url = hyperledger + "elections?filter="  + Filter.upcomming_filter();
        result = requests.get(url)
        return result.json(), result.status_code
    


    def get_ballot(self,electionId):

        """
        Returns a specific ballot for that voter
        """
        ballotId = self.voter +"_" + electionId
        url = hyperledger + "ballots/" + ballotId;
        result = requests.get(url)
        return result.json(),result.status_code


    def vote(self,electionId,answer):
        """
        Lets a user vote in an election
        """
        url = hyperledger + "vote";
        voter = "org.hyperledger_composer.ballots.voters#" + self.voter;
        election = "org.hyperledger_composer.ballots.elections#" + electionId;
        data = {
            "$class": "org.hyperledger_composer.ballots.vote",
            "voter": voter,
            "election":election,
            "answers": answer
            }

        result = requests.post(url,data)
        return result.json(),result.status_code




