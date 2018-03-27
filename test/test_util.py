#!/usr/bin/env python3
#
# test/test_util.py
# Authors:
#   Samuel Vargas
#

from typing import List
from src.crypto_suite import ECDSAKeyPair
import json


def generate_election_post_data(election_title: str = None,
                                description: str = None,
                                start_date: int = None,
                                end_date: int = None,
                                creator_keys: ECDSAKeyPair = None,
                                questions: List[List] = None):
    assert creator_keys and questions

    master_ballot_json_str = json.dumps({
        "election_title": election_title,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "questions": questions,
    })

    return {
        "master_ballot": master_ballot_json_str,
        "creator_public_key": creator_keys.get_public_key_b64().decode('utf-8'),
        "master_ballot_signature": creator_keys.sign_with_private_key_and_retrieve_b64_signature(
            master_ballot_json_str.encode('utf-8')).decode('utf-8')
    }


def generate_voter_post_data(election_title: str = None,
                             voter_keys: ECDSAKeyPair = None,
                             answers: List = None):
    ballot_json_str = json.dumps({
        "election_title": election_title,
        "answers": answers
    })

    return {
        "ballot": ballot_json_str,
        "voter_public_key": voter_keys.get_public_key_b64().decode('utf-8'),
        "ballot_signature": voter_keys.sign_with_private_key_and_retrieve_b64_signature(
            ballot_json_str.encode('utf-8')).decode('utf-8')
    }
