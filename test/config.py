#!/usr/bin/env python3
#
# test/config.py
# Authors:
#   Samuel Vargas
#

from src.sqlite.sqlite_backend_io import SQLiteBackendIO
#from src.hyperledger.hyperledger_backend_io import HyperledgerBackendIO

def test_backend():
    # @Alex replace this with a call to your HyperledgerBackendIO()
    # prior to running the testing suite
    return SQLiteBackendIO(":memory:")