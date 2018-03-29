#!/usr/bin/env python3
#
# src/interfaces/backend_io.py
# Authors:
#     Samuel Vargas

from typing import Optional, Dict
import abc


class BackendIO(abc.ABC):

    @abc.abstractmethod
    def create_election(self, master_ballot: Dict = None,
                        creator_username: str = None,
                        creator_master_ballot_signature: str = None,
                        creator_public_key_b64: str = None,
                        election_private_rsa_key: str = None,
                        election_public_rsa_key: str = None,
                        election_encrypted_fernet_key: str = None):
        raise NotImplementedError

    @abc.abstractmethod
    def create_ballot(self, ballot: str,
                            ballot_signature: str = None,
                            voter_public_key_b64: str = None):
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
