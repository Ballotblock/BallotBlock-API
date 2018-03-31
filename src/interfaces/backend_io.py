#!/usr/bin/env python3
#
# src/interfaces/backend_io.py
# Authors:
#     Samuel Vargas

from typing import Optional, List, Dict
import abc


class BackendIO(abc.ABC):

    @abc.abstractmethod
    def create_election(self, master_ballot: Dict = None,
                        creator_username: str = None,
                        creator_master_ballot_signature_b64: str = None,
                        creator_public_ecdsa_key_b64: str = None,
                        election_private_rsa_key_b64: str = None,
                        election_public_rsa_key_b64: str = None,
                        election_encrypted_fernet_key_b64: str = None):
        """
        Create an election on the backend:

        The "election_title" inside of the master_ballot dictionary is used
        to uniquely identify any given election.

        All of the following data should be stored


        :param master_ballot: A dictionary with the following format:
                              {
                                  "description": "Pick your favorite color / shape.",
                                  "election_title": "Favorite Color and Shape Election",
                                  "start_date": 1521507388,
                                  "end_date": 1522371388,
                                  "questions": [
                                      ["Favorite Color?", ["Red", "Blue"]],
                                      ["Favorite Shape?", ["Square", "Triangle"]]
                                   ]
                              }

        :param creator_username: The individual who created this election.
                                 The creator_username should be associated with the election.

        :param creator_master_ballot_signature_b64: It's the signed version of the "master_ballot" dictionary
                                                    in string format

        :param creator_public_ecdsa_key_b64: The creator's public ECDSA key in base64 format.

        :param election_private_rsa_key: The election's private RSA key in base64 format.

        :param election_public_rsa_key: The election's public RSA key in base64 format.

        :param election_encrypted_fernet_key_b64: The election's encrypted symmetric fernet key in base64 format.


        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_ballot(self, ballot: str,
                            ballot_signature_b64: str = None,
                            voter_public_key_b64: str = None):
        """
        :param ballot: A dictionary with the following format
                       {
                        'election_title': 'The Favorite Color and Shape Election',
                        'answers': '['Red', 'Triangle']'
                       }

        :param ballot_signature_b64: A base64 encoded ballot signature
        :param voter_public_key_b64: A base64 encoded voter_public_key_b64
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_election_by_title(self, election_title: str) -> Optional[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_ballot_by_voter_uuid(self, voter_uuid: str) -> Optional[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def register_user_as_participated_in_election(self, username: str, election_title: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def has_user_participated_in_election(self, username: str, election_title: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_ballots(self, election_title) -> List[Dict]:
        """
        This function should a return a list of dictionaries
        of all the ballots that are associated with a given
        Election.

        The return'd list should look similar to this:
         [
            {
              "voter_uuid": "This voter's uuid",
              "ballot": "Encrypted string"
              "ballot_signature": "The ballot signature"
              "election_title": "Title of the election",
            },

            { 'ballot':  "...",
              "voter_uuid" : "...",
              "ballot" : "...",
              "ballot_signature" : "...",
              "election_title" : "..."
            },

            ...
         ]

        :param election_title: The title of the election, guaranteed to exist
                               as 'get_election_by_title' is called prior to
                               this function being used.

        :return: A list of all the ballots stored on the backend.
        """
        raise NotImplementedError
