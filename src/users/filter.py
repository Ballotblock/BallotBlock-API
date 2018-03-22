#
# src/users/filter.py
# Authors:
#     Alex Gao
#


import datetime
import json

# this class is for generating filters to use in querying data through Hyperledger Composer REST API
# this follows LoopBack syntax
class Filter() :

    def current_filter(self):
        """
        Generates a filter query parameter to retrieve all current elections
        These filters are submitted are submitted through the Hyperledger Composer Rest API
        Only the electionIds are returned to keep messages smaller
        Example of generated string:
        {"fields": {"electionId": true}, "where": {"and": [{"endDate": {"gt": "2018-03-21T22:17:06.852272"}}, {"startDate": {"lt": "2018-03-21T22:17:06.852272"}}]}}
        """
        current_date = datetime.datetime.now().isoformat();

        filter = {
            "fields": {"electionId" : True},
            "where" : {
                   "and": [
                       {"endDate":{
                           "gt":current_date
                           }},
                       {"startDate": {
                           "lt":current_date
                           }}
                       ]
                }
            }
        return json.dumps(filter);

    def past_filter(self):
        """
        Generates a filter query parameter to retrieve all past elections
        These filters are submitted are submitted through the Hyperledger Composer Rest API
        Only the electionIds are returned to keep messages smaller
        """
        current_date = datetime.datetime.now().isoformat();
        
        filter = {
            "fields":{"electionId":True},
            "where": {
                "endDate":{
                    "lt":current_date
                    }
                }
            }
        return json.dumps(filter);

    def upcomming_filter(self):
        """
        Generates a filter query parameter to retrieve all upcomming elections
        These filters are submitted are submitted through the Hyperledger Composer Rest API
        Only the electionIds are returned to keep messages smaller
        """
        current_date = datetime.datetime.now().isoformat();
        
        filter = {
            "fields":{"electionId":True},
            "where": {
                "endDate":{
                    "gt":current_date
                    }
                }
            }
        return filter;





