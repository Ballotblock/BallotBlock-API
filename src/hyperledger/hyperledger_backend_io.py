
# HyperledgerBackendIO is responsible for interactiong with a deployed
# hyperledger composer rest server that is tied to a hyperledger blockchain 
# platform of your choice
#
# The Hyperledger Composer Rest server is created independently as a separate backend,
# in this specific backend choice a fabric network is used and a specific peer channel
# in the network is mapped to the business network defined in the hyperledger composer 
# model. Due to the fact that python was choosen, integration is done using a 
# rest server. Note that there are other SDKs that can be used to interact with composer
# not using the composer rest server
#
# Due to the fact that hyperledger is meant to be a private permissioned 
# blockchain, this particular interface implementation will not use any 
# outside signatures or encryption as this is managed in the deployment process
# and within the hyperledger network itself


import requests
from urllib.parse import quote
from flask import json
from .filter import Filter


class HyperledgerBackendIO() :
    def __init__(self,url):
        self.hyperledger = url
    
    def create_election(creator,electionTitle,propositions,startDate,endDate):
        raise NotImplementedError

    def create_ballot(self,voter,electionId,answer):
        """
        Lets a user vote in an election by creating a ballot
        The following parameters are:
            - voter : a voters voterId , it can be same as the username
            - electionId : the title of an election
            - answer: an array of integers, each integer corresponding to a specific 
            choice in a proposition for the election
        """
        url = self.hyperledger + "vote"
        voter = "org.hyperledger_composer.ballots.voters#" + voter
        election = "org.hyperledger_composer.ballots.elections#" + electionId
        data = {
            "$class": "org.hyperledger_composer.ballots.vote",
            "voter": voter,
            "election":election,
            "answers": answer
            }

        result = requests.post(url,data)
        return result.json(),result.status_code

    def get_election_by_title(self,voter,electionId):
        """
        Lets a user retrieve the details of an election and their involvement
        The following parameters are:
            - voter: a voters voterId
            - electionId: title of the elction

        Returns a voter's selections in their ballot for the election if 
        that ballot exists. The ballot exists if they have voted for that election.

        It then returns all the details of the election including:
        - startDate 
        - endDate
        - organizer : the creator of the election
        - propositions: a list of questions, each question has a sublist of choices
        """
        url = self.hyperledger + "elections/" + electionId
        result = requests.get(url)

        ballotId = voter +"_" + electionId;
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

    def get_current_elections(self) :
        """
        Returns the current elections in the hyperledger backend
        Only the electionId(s) are returned to limit packet size
        """
        url = self.hyperledger + "elections?filter="  + Filter.current_filter();
        result = requests.get(url)
        return result.json(), result.status_code

    def get_past_elections(self):
         """
        Returns the past elections in the hyperledger backend
        """

        url = hyperledger + "elections?filter="  + Filter.past_filter();
        result = requests.get(url)
        return result.json(), result.status_code


    def get_upcomming_elections(self):
       """
        Returns the upcomming elections in the hyperledger backend
        """

        url = hyperledger + "elections?filter="  + Filter.upcomming_filter();
        result = requests.get(url)
        return result.json(), result.status_code

    def get_election_results(self,electionId):
        """
        Parameters are :
        - electionId : the title essentially for an election

        ToDo:
        - retrieve the elections object, check if the endDate has passed
        - check to see if results has been tallied
        - if not tallied, retrieve all the ballots for that election
        - loop through and get the results
        - update the election object using put command on hyperledger
        - return the election object to the requesting client
        """

        raise NotImplementedError;



                                                        )
