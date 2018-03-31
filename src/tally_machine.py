#!/usr/bin/env python3
#
# src/tally_machine.py
# Authors:
#     Samuel Vargas
#

import json
from typing import List, Dict


class TallyMachine:
    @staticmethod
    def tally_election_ballots(questions: List, ballots: List[Dict]) -> Dict:
        """
        :param questions Should be in the following format:

        [
            ["Question 1", ["Option A,", "Option B", "Option C"]],
            ["Question 2", ["Option A,", "Option C"]],
            ....
        ]

        :param ballots: Should be in the following format:
                        [
                            {
                                "voter_uuid": '235797e1-00f2-4981-a500-98686b96a47b',
                                "ballot": ''{"election_title": "TallyingTest", "answers": ["Red", "Triangle"]}''
                                "ballot_signature", "ALjfdsalkfjsdlksdalfjsdlkfj==",
                                "election_title", "The Election Title",
                            },

                            {
                                "voter_uuid" : "...",
                                "ballot" : "...",
                                "ballot_signature" : "...",
                                "election_title", "..."
                                ...
                            }

                            ...
                        ]

        :return: Returns a List of dicts in the following format:
                 {
                    "participant_count" : 48
                    "questions" :
                    [
                        {
                        "Favorite Color?" :
                            {
                                "Red" : 32
                                "Blue" : 16
                            },
                        },

                        {
                        "Favorite SHape?" :
                            {
                                "Triangle" : 40
                                "Square" : 8
                            },
                        },


                        ....

                     ]
                 }
        """

        tally_results = []
        # For each question in the election
        answer_index = 0
        for q in questions:
            # Make the question itself the key, the value an empty dictionary of summed answers
            tally_results.append({q[0] : {}})
            # For each person who voted
            for ballot in ballots:
                # Get the value the user chose for this question
                answer = json.loads(ballot['ballot'])['answers'][answer_index]
                # Increment the count of people who chose this answer
                tally_results[-1][q[0]][answer] = tally_results[-1][q[0]].get(answer, 0) + 1

            # If nobody voted manually insert a {'Unpopular' : 0 }
            for choice in q[1]:
                if choice not in tally_results[-1][q[0]]:
                    tally_results[-1][q[0]][choice] = 0

            answer_index = answer_index + 1

        return {
            "participant_count": len(ballots),
            "questions": tally_results
        }
