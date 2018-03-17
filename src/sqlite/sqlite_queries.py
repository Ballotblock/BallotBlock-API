#!/usr/bin/env python3
#
# src/sqlite3/sqlite_queries.py
# Authors:
#     Samuel Vargas

#
# Creation
#

#  MasterBallot and Election have a 1:1 correspondence.
#  Ballots and MasterBallots have a Many to 1 correspondence.

CREATE_MASTER_BALLOT_TABLE = """
CREATE TABLE IF NOT EXISTS MasterBallot
(master_ballot_id TEXT NOT NULL UNIQUE,
 election_id      TEXT NOT NULL UNIQUE,
 questions        TEXT NOT NULL,
                  FOREIGN KEY (election_id) REFERENCES Election(election_id)
                  PRIMARY KEY(master_ballot_id))
"""

CREATE_ELECTION_TABLE = """
CREATE TABLE IF NOT EXISTS Election
(election_id       TEXT NOT NULL UNIQUE,
 creator_id        TEXT NOT NULL UNIQUE,
 title             TEXT NOT NULL UNIQUE,
 description       TEXT NOT NULL,
 start_date        INT NOT NULL,
 end_date          INT NOT NULL,
 master_ballot_id  TEXT NOT NULL UNIQUE,
                   FOREIGN KEY (master_ballot_id) REFERENCES MasterBallot(master_ballot_id)
                   PRIMARY KEY(election_id))
"""

# Answers is a JSON Dump for now.
CREATE_BALLOT_TABLE = """
CREATE TABLE IF NOT EXISTS Ballot
(ballot_id         TEXT NOT NULL UNIQUE,
 answers           TEXT NOT NULL,
 master_ballot_id  TEXT NOT NULL UNIQUE,
                   FOREIGN KEY (master_ballot_id) REFERENCES MasterBallot(master_ballot_id)
                   PRIMARY KEY(ballot_id))
"""

#
# Insertion
#

INSERT_MASTER_BALLOT = """
INSERT INTO MasterBallot (
    master_ballot_id,
    election_id,
    questions)
VALUES(?, ?, ?)
"""

INSERT_ELECTION = """
INSERT INTO Election (
     election_id,
     creator_id,
     title,
     description,
     start_date,
     end_date,
     master_ballot_id)
VALUES(?, ?, ?, ?, ?, ?, ?)
"""

INSERT_BALLOT = """
INSERT INTO Ballot (
     ballot_id,
     answers,
     master_ballot_id)
VALUES(?, ?, ?)
"""
