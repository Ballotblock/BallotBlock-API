#!/usr/bin/env python3
#
# src/sqlite3/sqlite_queries.py
# Authors:
#     Samuel Vargas

#
# Creation
#

# List of all elections in the system.
# private_key should only be returned to the api caller if start_date >= end_date
CREATE_ELECTION_TABLE = """
CREATE TABLE IF NOT EXISTS Election
(election_title                 TEXT NOT NULL UNIQUE,
 description                    TEXT NOT NULL,
 start_date                     INT NOT NULL,
 end_date                       INT NOT NULL,
 questions                      TEXT NOT NULL,
 creator_username               TEXT NOT NULL,
 master_ballot_signature        TEXT NOT NULL,
 creator_public_key             TEXT NOT NULL,
 election_public_key            TEXT NOT NULL UNIQUE,
 election_private_key           TEXT NOT NULL UNIQUE,
 election_encrypted_fernet_key  TEXT NOT NULL UNIQUE,
                                PRIMARY KEY(election_title))
"""

# Records which elections a user has participated in.
# Used to prevent a user from voting in the same election twice.
CREATE_ELECTION_PARTICIPATION_TABLE = """
CREATE TABLE IF NOT EXISTS ElectionParticipation
(election_title TEXT NOT NULL,
 username       TEXT NOT NULL,
                FOREIGN KEY(election_title) REFERENCES Election(election_title)
                PRIMARY KEY(election_title))
"""

# An individual ballot
CREATE_BALLOT_TABLE = """
CREATE TABLE IF NOT EXISTS Ballot
(voter_uuid          TEXT NOT NULL UNIQUE,
 ballot              TEXT NOT NULL,
 election_title      TEXT NOT NULL,
                     FOREIGN KEY(election_title) REFERENCES Election(election_title)
                     PRIMARY KEY(voter_uuid))
"""

#
# Insertion
#

INSERT_ELECTION = """
INSERT INTO Election (
     election_title,
     description,
     start_date,
     end_date,
     questions,
     creator_username,
     master_ballot_signature,
     creator_public_key,
     election_public_key,
     election_private_key,
     election_encrypted_fernet_key)
VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

INSERT_ELECTION_PARTICIPATION = """
INSERT INTO ElectionParticipation (
    election_title,
    username)
VALUES(?, ?)
"""

INSERT_BALLOT = """
INSERT INTO Ballot (
     voter_uuid,
     ballot,
     election_title)
VALUES(?, ?, ?)
"""

#
# Searching / Retrieval
#

SELECT_ELECTION_BY_TITLE = """
SELECT * from Election WHERE
    election_title = (?)
"""

SELECT_BALLOT_BY_VOTER_UUID = """
SELECT * from Ballot WHERE
    voter_uuid = (?)
"""

SELECT_ELECTION_PARTICIPATION_BY_USERNAME = """
SELECT * from ElectionParticipation WHERE
    username = (?)
"""
