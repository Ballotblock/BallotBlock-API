#!/usr/bin/env python3
#
# src/interfaces/backend_io.py
# Authors:
#     Samuel Vargas

from typing import Optional, Dict
import abc


class BackendIO(abc.ABC):
    @abc.abstractmethod
    def create_election(self, election_details: Dict):
        """
        Receives a dictionary with the following schema:
        :param election_details:
        {
            "election_title": "The Favorite Color and Shape Election",
            "description": "This is the description of this Election",
            "start_date": 1380238023 (unix timestamp),
            "end_date": 32808320 (unix timestamp),
            "creator_username": "Username",
            "questions:" "[
                ["Favorite Color?", ["Red", Blue]],
                ["Favorite Shape?", ["Square", "Triangle]]
            ]",
            "public_key": "Public key for the entire election",
            "private_key": "Private key for the entire election,
        }
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_ballot(self, ballot: Dict):
        """
        Receives a dictionary with the following schema:

        :param ballot:
        {
            "voter_id" "uuid4",
            "election_title": "The Favorite Color and Shape Election",
            "answers": "['Red', 'Triangle']"
        }

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_election_by_title(self, election_title: str) -> Optional[Dict]:
        """
        Should return a dictionary from the backend with the following schema:

        :param election_title The title of the election.

        :return:
        {
            "election_title": "The Favorite Color and Shape Election",
            "description": "This is the description of this Election",
            "start_date": 1380238023 (unix timestamp),
            "end_date": 32808320 (unix timestamp),
            "creator_username": "Username",
            "questions:" "[
                ["Favorite Color?", ["Red", Blue]],
                ["Favorite Shape?", ["Square", "Triangle]]
            ]",
            "public_key": "Public key for the entire election",
            "private_key": "Private key for the entire election,
        }
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_ballot_by_id(self, voter_id: str) -> Optional[Dict]:
        """
        Should return a dictionary with the following schema:
        :param voter_id: The voter ID that corresponds to a specific ballot, should be a uuid4
        :return:
        {
            "voter_id" "uuid4",
            "election_title": "The Favorite Color and Shape Election",
            "answers": "['Red', 'Triangle']"
        }
        """
        raise NotImplementedError
