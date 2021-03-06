#!/usr/bin/env python3
#
# src/sqlite3/sqlite_backend_io.py
# Authors:
#     Samuel Vargas

#
# SQLiteBackendIO is responsible for:
#  [*] Storing and retrieving data about Elections / Individual Ballots / MasterBallots
#  [*] Preventing an Election with the same election_id / title from being created.
#  [*] Preventing a MasterBallot with the same master_ballot_id from being created.
#
# It is NOT responsible for:
#  [*] Verifying that all keys are present in master_ballot / election_details (KeyError will be thrown)
#  [*] Verifying that the data itself is valid
#
# These tasks are the responsibility of the host application.

# TODO
#   * Verify that all types are correct (strings and ints) when data is passed in
#   * Verify that dictionaries do not contain extra keys


from typing import Optional, Dict, List
from src.interfaces.backend_io import BackendIO
from .sqlite_queries import *
import sqlite3
import json


class SQLiteBackendIO(BackendIO):

    def __init__(self, db_path):
        super().__init__()
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute(CREATE_ELECTION_TABLE)
        self.cursor.execute(CREATE_ELECTION_PARTICIPATION_TABLE)
        self.cursor.execute(CREATE_BALLOT_TABLE)
        self.connection.commit()

    def create_election(self, master_ballot: Dict = None,
                        creator_username: str = None,
                        creator_master_ballot_signature: str = None,
                        creator_public_key_b64: str = None,
                        election_public_rsa_key: str = None,
                        election_private_rsa_key: str = None,
                        election_encrypted_fernet_key: str = None):

        assert creator_username and creator_master_ballot_signature and \
               creator_master_ballot_signature and creator_public_key_b64 and \
               election_private_rsa_key and election_public_rsa_key and election_encrypted_fernet_key

        if self.get_election_by_title(master_ballot['election_title']) is not None:
            raise ValueError("Can't create duplicate election.")

        self.cursor.execute(INSERT_ELECTION, (
            master_ballot['election_title'],
            master_ballot['description'],
            master_ballot['start_date'],
            master_ballot['end_date'],
            master_ballot['questions'],
            creator_username,
            creator_master_ballot_signature,
            creator_public_key_b64,
            election_public_rsa_key,
            election_private_rsa_key,
            election_encrypted_fernet_key
        ))

        self.connection.commit()

    def create_ballot(self, ballot: str,
                      election_title: str = None,
                      voter_uuid: str = None,
                      ballot_signature: str = None,
                      voter_public_key_b64: str = None):

        assert election_title and voter_uuid and \
               ballot_signature and voter_public_key_b64

        result = self.get_election_by_title(election_title)
        if result is None:
            raise ValueError("Can't create ballot for non-existent election")

        self.cursor.execute(INSERT_BALLOT, (
            voter_uuid,
            ballot,
            ballot_signature,
            election_title,
        ))

        self.connection.commit()

    def get_election_by_title(self, election_title: str) -> Optional[Dict]:
        self.cursor.execute(SELECT_ELECTION_BY_TITLE, (election_title,))
        result = self.cursor.fetchone()
        if result is None:
            return None

        output = {
            "election_title": result[0],
            "description": result[1],
            "start_date": result[2],
            "end_date": result[3],
            "questions": result[4],
            "creator_username": result[5],
            "master_ballot_signature": result[6],
            "creator_public_key": result[7],
            "election_public_key": result[8],
            "election_private_key": result[9],
            "election_encrypted_fernet_key": result[10]
        }

        return output

    def get_ballot_by_voter_uuid(self, voter_uuid: str):
        self.cursor.execute(SELECT_BALLOT_BY_VOTER_UUID, (voter_uuid,))
        result = self.cursor.fetchone()
        if result is None:
            return None

        return {
            "voter_uuid": result[0],
            "ballot": result[1],
            "ballot_signature": result[2],
            "election_title": result[3]
        }

    def register_user_as_participated_in_election(self, username: str, election_title: str):
        if self.get_election_by_title(election_title) is None:
            raise ValueError("Can't register user as having participated in non-existent election")
        self.cursor.execute(INSERT_ELECTION_PARTICIPATION, (election_title, username,))
        self.connection.commit()

    def has_user_participated_in_election(self, username: str, election_title: str) -> bool:
        if self.get_election_by_title(election_title) is None:
            raise ValueError("Can't check if user has participated in non-existent election")
        self.cursor.execute(SELECT_ELECTION_PARTICIPATION_BY_USERNAME, (username,))
        result = self.cursor.fetchone()
        return result is not None

    def get_all_ballots(self, election_title) -> List[Dict]:
        assert self.get_election_by_title(election_title) is not None
        self.cursor.execute(SELECT_ALL_BALLOTS, (election_title,))
        output = []
        for result in self.cursor.fetchall():
            output.append({
                "voter_uuid": result[0],
                "ballot": result[1],
                "ballot_signature": result[2],
                "election_title": result[3]
            })

        return output

    def get_all_elections(self):
        self.cursor.execute(SELECT_ALL_ELECTIONS)
        output = []
        for result in self.cursor.fetchall():
            output.append({
                "election_title": result[0],
                "description": result[1],
                "start_date": result[2],
                "end_date": result[3],
                "questions": result[4],
                "creator_username": result[5],
                "master_ballot_signature": result[6],
                "creator_public_key": result[7],
                "election_public_key": result[8],
                "election_private_key": result[9],
                "election_encrypted_fernet_key": result[10]
            })
        return output

    def nuke(self):
        self.cursor.execute(DELETE_ALL_BALLOT)
        self.cursor.execute(DELETE_ALL_ELECTION)
        self.cursor.execute(DELETE_ALL_ELECTION_PARTICIPATION)
        self.connection.commit()

    def close(self):
        self.connection.close()
