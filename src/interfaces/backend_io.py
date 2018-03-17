#!/usr/bin/env python3
#
# src/interfaces/backend_io.py
# Authors:
#     Samuel Vargas

from typing import Optional, Dict
import abc


class BackendIO(abc.ABC):
    @abc.abstractmethod
    def create_election(self, master_ballot: Dict, election_details: Dict):
        raise NotImplementedError

    @abc.abstractmethod
    def get_election_details(self, election_id: str) -> Dict:
        raise NotImplementedError

    @abc.abstractmethod
    def find_election_by_title(self, election_title: str) -> Optional[Dict]:
        # Given a particular title,
        raise NotImplementedError()
