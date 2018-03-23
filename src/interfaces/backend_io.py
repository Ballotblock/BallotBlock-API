#!/usr/bin/env python3
#
# src/interfaces/backend_io.py
# Authors:
#     Samuel Vargas

from typing import Optional, Dict
import abc


class BackendIO(abc.ABC):
    @abc.abstractmethod
    def create_election(self, master_ballot: Dict,
                        creator_master_ballot_signature: str = None,
                        creator_public_key_hex: str = None,
                        backend_public_key_hex: str = None,
                        backend_private_key_hex: str = None):
        raise NotImplementedError

    @abc.abstractmethod
    def create_ballot(self, ballot: Dict):
        raise NotImplementedError

    @abc.abstractmethod
    def get_election_by_title(self, election_title: str) -> Optional[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_ballot_by_id(self, voter_id: str) -> Optional[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def has_user_participated_in_election(self, username: str, election_title: str) -> bool:
        raise NotImplementedError
