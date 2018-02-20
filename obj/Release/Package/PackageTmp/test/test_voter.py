#
# src/test_voter.py
# Authors:
#   Alex Gao
#

import unittest
from src.voter import voter

class VoterTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.user = voter("Alice")
        self.electionId = "ASASU2017 Election"

    def test_get_ballot(self):
        result = self.user.get_ballots()
        self.assertEqual(result[1],200)

    def test_get_election(self):
        result = self.user.get_elections(self.electionId)
        self.assertEqual(result[1],200)