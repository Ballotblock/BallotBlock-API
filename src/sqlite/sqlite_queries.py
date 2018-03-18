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
(master_ballot_title TEXT NOT NULL UNIQUE,
 questions           TEXT NOT NULL,
                     FOREIGN KEY (master_ballot_title) REFERENCES Election(election_title)
                     PRIMARY KEY(master_ballot_title))
"""

CREATE_ELECTION_TABLE = """
CREATE TABLE IF NOT EXISTS Election
(election_title      TEXT NOT NULL UNIQUE,
 description         TEXT NOT NULL,
 start_date          INT NOT NULL,
 end_date            INT NOT NULL,
 creator_id          TEXT NOT NULL UNIQUE,
 master_ballot_title TEXT NOT NULL UNIQUE,
                     FOREIGN KEY (master_ballot_title) REFERENCES MasterBallot(master_ballot_title)
                     PRIMARY KEY(election_title))
"""

# Answers is a JSON Dump for now.
CREATE_BALLOT_TABLE = """
CREATE TABLE IF NOT EXISTS Ballot
(ballot_id           TEXT NOT NULL UNIQUE,
 answers             TEXT NOT NULL,
 master_ballot_title TEXT NOT NULL UNIQUE,
                     FOREIGN KEY (master_ballot_title) REFERENCES MasterBallot(master_ballot_title)
                     PRIMARY KEY(ballot_id))
"""

#
# Insertion
#

INSERT_MASTER_BALLOT = """
INSERT INTO MasterBallot (
    master_ballot_title,
    questions)
VALUES(?, ?)
"""

INSERT_ELECTION = """
INSERT INTO Election (
     election_title,
     description,
     start_date,
     end_date,
     creator_id,
     master_ballot_title)
VALUES(?, ?, ?, ?, ?, ?)
"""

INSERT_BALLOT = """
INSERT INTO Ballot (
     ballot_id,
     answers,
     master_ballot_title)
VALUES(?, ?, ?)
"""

#
# Searching
#

SELECT_ELECTION_BY_TITLE = """
SELECT * from Election WHERE
    election_title = (?)
"""

SELECT_MASTER_BALLOT_BY_TITLE = """
SELECT * from MasterBallot WHERE
    master_ballot_title = (?)
"""
