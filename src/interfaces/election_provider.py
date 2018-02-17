#!/usr/bin/env python3
#
# src/server.py
# Authors:
#     Samuel Vargas

import abc


class ElectionProvider(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_election_details(self, election_id: str):
        """
        Given an election ID return details about the
        election itself. E.g.

        return {
            "start_date" : timestamp,
            "end_date" : timestamp,
            "Description", "This election is for..."
        }

        :param election_id: A uuid corresponding to an election
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_election_ballots(self, id: str):
        """
        Given an election ID return the list of ballots
        that everyone has casted so far in this particular
        election. This data should be returned (and stored)
        encrypted

        return {
            {
                "voter_id":  "readable_uuid",
                "user_identity": "encrypted with users public key, can only be decrypted by end user"
                "ballot": "encrypted using this voters public ballot key, will be dumped along with the voter's
                           voter_id at the end of the election.
            },

            {
            ...
            }
        }

        :param election_id:
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_election_single_ballot(self, election_id: str, voter_id: str):
        """
        Same as get_election_ballots but only returns a single
        ballot. Use it in the situation where an individual user
        wants to get their sent ballot to review it for some reason.
        :param election_id:
        :return:
        """
        raise NotImplementedError()

    @abc.abstractclassmethod
    def cast_election_ballot(self, election_id: str, voter_id: str, ballot):
        """
        Add a ballot to the election
        :param ballot:
        :return:
        """
        raise NotImplementedError()
