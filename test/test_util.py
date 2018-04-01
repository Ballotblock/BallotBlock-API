#!/usr/bin/env python3
#
# test/test_util.py
# Authors:
#   Samuel Vargas
#

from typing import List
from src.crypto_suite import ECDSAKeyPair
import json

# Random RSA key and Fernet Key (encrypted using the public_key)
# Use it in tests that create elections by mocking out
# 'CryptoFlow.generate_election_creator_rsa_keys_and_encrypted_fernet_key_dict = \
#  MagicMock(return_value=ELECTION_DUMMY_RSA_FERNET)

ELECTION_DUMMY_RSA_FERNET = {
    'election_encrypted_fernet_key': 'y1WxjSR8tpT0eKtoGusJ79xpQJCBYmAL7Lde4MFRuEwqACwtVYxPuhA0KXVudfxF+rhlIoiT+FbsU0K6By3KcpvGDJqtPjkMmOtWfR1fs9aR6uHjh+ADr/BVHeuMZqW6cmYE3klXUn2QusfRXbRuT+bmGFU3PqjKTWNT4ycsY5twQY8tNow8M+Z57hojGUe5YXrb0jD8fqCBbN5aDR7lfiUN/mvLm30B7dpifuI47dM82psdl1VgGlmh7WEFo8PR+p0xhrGu6Vv7meL5ZOeA6gRRiDhXJhZtCn6C9jQ4tFypTefI5Tmzh2VWdS2xBXYCp6srV/XkPVLsl5tMNOCukg==',
    'election_private_key': 'LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcWdJQkFBS0NBUUVBNExNdHMrVFFxUllFRk41WUlHUnJFZUlBNTFJRTRHR1RmWm92NEFnS1hYbk9nNE93CmI5ZTkrQml6bDRGR2pvRmJIUk8xTlR0amN4c3hTWEI0eUhvemhxUm1GMm9wZSs1ZVFNTHFwQjNtek05R1hKZisKWTJtdkdNWG5WQ2hnWEhiTzhtZDBWUTdQYS9lUStDaWxRcHErZjNIdWl2cHJuLzBNb1U3NXdCaUZMT29oeWlMOQpTcEZMdlVZSVhGbDA3Zk4zSnpyQ2xCYzM5TXU4djE3RHF2cUh6VXE3aVJRVnJ1ZWttdk04UFc3eVpaT0lzRnlwCmtadFpKMmxsSkYxMnl6Tytnb1pZV3VoQ2FFVFpiRllOaDdVc2Q0anFmdmk3dDZKSkltS3E3VUNuQ3VsZW5nYVgKc0dQL2lLcVJUUXZDSG1jRFlaL1o1KytpVkZXSnV6RVptRS8vQlFJREFRQUJBb0lCQVFEVVM1WFBsRTBzbzlkaApYQjFKSlhjZm96Y1ZWcUd5MlozL0dwRkhDbkc0bFYvdlU1bDhZZ3BpLy91V0ZoYnlodmJ0eHZQN0FreFlzWVZrCmpIWWhlNHQ1RjVRNVpSMGlzVGl0MlRyVnFrYW9sT0UybEloTnBzay9ENlFiR0RiS3habUszd0hEWjBYRURWZ1QKamx0dFRVVFVwbkVwTDZaRnQwKzlHbVZmR1l3U3c5cGFRSjN3QnZuc01iZ2FJK0lrTThsVmg0NE5lTjQ1L0cxVApZYlVVNllodGdRTi8xMk9ET2VZRVEwQnZ2TFNPWTdXdDRTV1BaakEvRGV0TGxQc3p5UVdGajZtWm1KeWhQdEZXCjhrWE0wZ1FiZjJ6a1dUVHZOT2Z1ejk0eHltRGJiVkVnYW53QlBaQVhReFoxZHVTQ0ZiUFhWdVc2eUR1WmV0aVYKdlRUVGkzVEJBb0dKQU9waFFwNGl5UWxvaXJSZGFINldYV2ZNM1dGQkxLYXU5SWtTUHNKQWlza3VtTWR0SnVaVworWXJTbDNZTmM3QktaY1FOWGRwS1JCVzBFVnNKSFEwbUNxM0ZJVnE4aEo2aGlKcWxDTlEvNTlieFplWG5xMUFRClVRcUVoNWFlYXBPS01YNjNZbHR1V3NSeDA4aEszUTErckpPZWxsbG05NDJxSkE4OUhkR3V1ZFoxWnl2TFdnVnkKY2JVQ2VRRDFiVlN3SnIxUWM4K2p2bEpoOFNRY2UrRTVsam1TRHEvNTZab0VBSGZPSVVnZVI3aGxESGNPMTZOcwpJbkkrTWkyWG1veisvem84Q1FsWDdVaFRkdk4vQ3RWKzNWUDRRTXF4WTk4ejhLSWlDeGk4aEFsZHd4cVVTRm1rCjMwWE5jMUZ5VHdUZTFhN1crQjJuL0hjc1VCOWFMZGhBVE9rTDZoRUNnWWtBdlNMYmRXMHd1aXpvc1lBblVPL2EKVkdkWHhxR25mS0wycHA1WWtyMHV3Z2FlTjJCMzRhMFNGdHEyYXdlVDhoRTNhaXczTG01NzN0KyttYTRUQ1lkSApXczhYaVhkVHRnYzRpMExlaXhrKzU0OUo0V3RBTFkzZE9CV1dyUThOaGg0Z3J0Y2h3aEtkb0tVU2VERWhqVUJKCjE1NUVTY1R6eEJnbW5UMStrTFRsTnBEclBzWU0wUlIzZVFKNGRHWFg1bnRaQ2hFREIxdTZZcTBsUFVVYmVsNWYKQzRCZndaMGk2SWI0U3hESnpXS2lkM3BEOVF3Y2U2cVNtQ0RnTXFpZitrZzk3RDgwNlRpbU5yK1JtRTBoR0R3TQpHUTlSa25RVlplTFlZbUQwNkdPT3RhTlV0Y0xpa1NrN1I4ZExkM1Uya0NDei9VeExkR0p1ZXR1OUl0M2ZWQStsCjczcWhBb0dJUFdDNWs4N0h0NGhKQkpLUnZaYnNBMy9qRjBnSTVjR0ZyRVZNZDRya2EwcW0ySGxVQ010d3VtNXoKOVlURW5aU2dHYnU1Q04zeXRBVFE0QWltdERtUGdzV2pLQTBtYlowNmtZSldpSVZSdDA4cCtYdi9TclFheW0xNQpMU2Z3a2ZYWW9EVkFDRW1sYm9HNnYwZ2V5TXZwUU9SdzdIdzd2cG1LOExEUlN6MU5PNEhIc3RCN3p6T2c3Zz09Ci0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg==',
    'election_public_key': 'LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1JSUJDZ0tDQVFFQTRMTXRzK1RRcVJZRUZONVlJR1JyRWVJQTUxSUU0R0dUZlpvdjRBZ0tYWG5PZzRPd2I5ZTkKK0Jpemw0Rkdqb0ZiSFJPMU5UdGpjeHN4U1hCNHlIb3pocVJtRjJvcGUrNWVRTUxxcEIzbXpNOUdYSmYrWTJtdgpHTVhuVkNoZ1hIYk84bWQwVlE3UGEvZVErQ2lsUXBxK2YzSHVpdnBybi8wTW9VNzV3QmlGTE9vaHlpTDlTcEZMCnZVWUlYRmwwN2ZOM0p6ckNsQmMzOU11OHYxN0RxdnFIelVxN2lSUVZydWVrbXZNOFBXN3laWk9Jc0Z5cGtadFoKSjJsbEpGMTJ5ek8rZ29aWVd1aENhRVRaYkZZTmg3VXNkNGpxZnZpN3Q2SkpJbUtxN1VDbkN1bGVuZ2FYc0dQLwppS3FSVFF2Q0htY0RZWi9aNSsraVZGV0p1ekVabUUvL0JRSURBUUFCCi0tLS0tRU5EIFJTQSBQVUJMSUMgS0VZLS0tLS0K'
}

def generate_election_post_data(election_title: str = None,
                                description: str = None,
                                start_date: str = None,
                                end_date: str = None,
                                creator_keys: ECDSAKeyPair = None,
                                questions: List[List] = None, **kwargs):
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
