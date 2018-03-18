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


from typing import Optional, Dict
from src.interfaces.backend_io import BackendIO
from .sqlite_queries import *
import sqlite3

REQUIRED_ELECTION_KEYS = (
    "election_title",
    "description",
    "start_date",
    "end_date",
    "creator_id",
    "master_ballot_title"
)

REQUIRED_MASTER_BALLOT_KEYS = (
    "master_ballot_title",
    "questions"
)

REQUIRED_BALLOT_KEYS = (
    "ballot_id",
    "answers",
    "master_ballot_title"
)

class SQLiteBackendIO(BackendIO):
    def __init__(self, db_path):
        super().__init__()
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute(CREATE_MASTER_BALLOT_TABLE)
        self.cursor.execute(CREATE_ELECTION_TABLE)
        self.cursor.execute(CREATE_BALLOT_TABLE)
        self.connection.commit()

    def create_election(self, master_ballot: Dict, election_details: Dict):
        for key in REQUIRED_ELECTION_KEYS:
            if key not in election_details:
                raise ValueError("Missing Key: '{0}'".format(key))

        for key in REQUIRED_MASTER_BALLOT_KEYS:
            if key not in master_ballot:
                raise ValueError("Missing Key: '{0}'".format(key))

        election_title = election_details["election_title"]
        if self.get_election_by_title(election_title) is not None:
            raise ValueError("Election with title '{id}' already exists".format(id=election_title))

        self.cursor.execute(
            INSERT_MASTER_BALLOT, (master_ballot["master_ballot_title"],
                                   master_ballot["questions"]
                                   )
        )

        self.cursor.execute(
            INSERT_ELECTION, (election_details["election_title"],
                              election_details["description"],
                              election_details["start_date"],
                              election_details["end_date"],
                              election_details["creator_id"],
                              election_details["master_ballot_title"]
                              )
        )

        self.connection.commit()

    def create_ballot(self, ballot: Dict):
        for key in REQUIRED_BALLOT_KEYS:
            if key not in ballot:
                raise ValueError("Missing Key: '{0}'".format(key))

        # If there is an election then there is a master ballot (Referential Integrity)
        if self.get_election_by_title(ballot["master_ballot_title"]) is None:
            raise ValueError("Can't add ballot, corresponding Election / MasterBallot not found.")

        self.cursor.execute(
            INSERT_BALLOT, (ballot["ballot_id"],
                            ballot["answers"],
                            ballot["master_ballot_title"]
                           )
        )

        self.connection.commit()

    def get_election_by_title(self, election_title: str) -> Optional[Dict]:
        self.cursor.execute(SELECT_ELECTION_BY_TITLE, (election_title,))
        result = self.cursor.fetchone()
        if result is None:
            return result

        return {
            "election_title": result[0],
            "description": result[1],
            "start_date": result[2],
            "end_date": result[3],
            "creator_id": result[4],
            "master_ballot_title": result[5]
        }

    def get_master_ballot_by_title(self, election_title: str) -> Optional[Dict]:
        self.cursor.execute(SELECT_MASTER_BALLOT_BY_TITLE, (election_title,))
        result = self.cursor.fetchone()
        if result is None:
            return result

        return {
            "master_ballot_title": result[0],
            "questions": result[1],
        }

    def get_ballot_by_id(self, ballot_id: str):
        self.cursor.execute(SELECT_BALLOT_BY_ID, (ballot_id,))
        result = self.cursor.fetchone()
        if result is None:
            return result

        return {
            "ballot_id": result[0],
            "answers": result[1],
            "master_ballot_title": result[2]
        }

    def close(self):
        self.connection.close()