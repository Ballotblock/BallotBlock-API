#!/usr/bin/env python3
#
# src/sqlite3/sqlite_election_provider.py
# Authors:
#     Samuel Vargas

from src.interfaces.election_provider import ElectionProvider


class SQLiteElectionProvider(ElectionProvider):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path

    def get_election_details(self, election_id: str):
        pass

    def get_election_ballots(self, id: str):
        pass

    def get_election_single_ballot(self, election_id: str, voter_id: str):
        pass

    def cast_election_ballot(self, election_id: str, voter_id: str, ballot):
        pass