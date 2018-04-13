
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
        """
        This url is the url of the hyperledger composer rest server
        It may of course be one that is live on a server somewhere or simply hosted locally
        """
        self.hyperledger = url
    
    def create_election(self,creator,electionTitle,propositions,startDate,endDate):
        """
        Lets a creator type user create an election
        This methods takes the following parameters:
            - creator : a creators userId, it is the same as the username used to login
            - electionTitle : title of the election
            - propositions : is an array of proposition, each proposition corresponds to a particular position
                and has a list of choices. Below is an example of a propositions json
                    "propositions": [{
                                            "question": "Senator for: Barret,the Honors College",
                                            "choices": [
                                                "Danielle Heffners",
                                                "Emily Beaman",
                                                "Joseph Briones",
                                                "Keyle Storm Cloud"
                                            ]
                                        },
                                        {
                                            "question": "Senator for: Ira A. Fulton Schools of Engineering",
                                            "choices": [
                                                "Caroline Kireopoulos",
                                                "Eyad Al Sulaimi"
                                            ]
                                        }]
            - startDate : the date that the election will start in iso 8601 format
            - endDate : the date that the election will end in iso 8601 format
        Implementation wise, this method will do a post request to the elections endpoint on the 
        hyperledger composer rest server, and thus creating the "resource" election 
        """
        url = self.hyperledger + "elections"
        data = {
            "electionId" : electionTitle,
            "organizer" : creator,
            "propositions" : propositions,
            "startDate" : startDate,
            "endDate":endDate,
            "results" : [-1]
            }
        result = requests.post(url,json=data)
        return result.json(), result.status_code

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
        - selections : an array of integerers corresponding to an answer in the choices 
            "selections is only returned 
        """
        url = self.hyperledger + "elections/" + electionId
        result = requests.get(url)

        ballotId = voter +"_" + electionId
        url2 = self.hyperledger + "ballots/" + ballotId + "?filter=" + Filter.ballot_filter()
        result2 = requests.get(url2)

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
        url = self.hyperledger + "elections?filter="  + Filter.past_filter();
        result = requests.get(url)
        return result.json(), result.status_code

    def get_upcomming_elections(self):
        """
        Returns the upcomming elections in the hyperledger backend
        """

        url = self.hyperledger + "elections?filter="  + Filter.upcomming_filter();
        result = requests.get(url)
        return result.json(), result.status_code

    def get_results(self,electionTitle):
        #first get the election to see if results have been tallied
        url = self.hyperledger + "elections/" + electionTitle
        result = requests.get(url)
        electionResultJson = result.json()

        electionResult = electionResultJson['results']
    
        # if election has not been tallied
        if electionResult[0] == -1 :
            # here we query all the ballots, and loop through them all
            # we also need to update the election object, so that the next 
            # request won't have to tally again

            propositions = electionResultJson['propositions']
            # print(propositions)
            tally = []
            questions = [] #each index corresponds to a question, and the value at the index corresponds to the number of choices for that question
            for prop in propositions:
                choices =  prop['choices']
                questions.append(len(choices));
                for choice in choices:
                    tally.append(0)


            electionTitle = quote(electionTitle)
            resource = "resource:org.hyperledger_composer.ballots.elections#" + electionTitle
            resource = quote(resource)
            url = self.hyperledger + "queries/getElectionBallots?election=" + resource
            result = requests.get(url)
            ballotJson = result.json()
            for ballot in ballotJson:
                selections = ballot['selections']
                print(selections)
                # update tally
                for i in range(len(selections)):
                    index = selections[i]
                    if( i  > 0):
                        index = questions[i-1]  + selections[i]
                    tally[index] += 1
    
            electionResultJson['results'] = tally

            #update hyperledger
            url = self.hyperledger + "elections/" + electionTitle
            response = requests.put(url,json=electionResultJson)
            print(response.json())
        return electionResultJson




