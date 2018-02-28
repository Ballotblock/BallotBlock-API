#!/usr/bin/env python3
#
# src/interfaces/sqlite_backend_initializer.py
# Authors:
#     Samuel Vargas

import sqlite3

MASTER_BALLOT_TABLE = """
CREATE TABLE IF NOT EXISTS MasterBallots
(master_ballot_id TEXT NOT NULL,
question_choices TEXT NOT NULL,
PRIMARY KEY(master_ballot_id))
"""

ELECTION_TABLE = """
CREATE TABLE IF NOT EXISTS Elections
(election_id TEXT NOT NULL,
 username TEXT NOT NULL,
 title TEXT NOT NULL,
 description TEXT NOT NULL,
 start_date int NOT NULL,
 end_date INT NOT NULL,
 master_ballot_id TEXT NOT NULL,
    FOREIGN KEY (master_ballot_id) REFERENCES MasterBallots(master_ballot_id)
 PRIMARY KEY(election_id))
"""

BALLOT_TABLE = """
CREATE TABLE IF NOT EXISTS Ballots
(ballot_id TEXT NOT NULL,
 question_answer TEXT NOT NULL,
 master_ballot_id TEXT NOT NULL,
    FOREIGN KEY (master_ballot_id) REFERENCES MasterBallots(master_ballot_id)
 PRIMARY KEY(ballot_id))
"""


class SQLiteBackendInitializer:
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute(MASTER_BALLOT_TABLE)
        self.cursor.execute(ELECTION_TABLE)
        self.cursor.execute(BALLOT_TABLE)
        self.connection.commit()
