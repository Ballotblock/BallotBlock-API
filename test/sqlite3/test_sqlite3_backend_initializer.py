#!/usr/bin/env python3
#
# src/test/sqlite_backend_initializer.py
# Authors:
#     Samuel Vargas

from src.sqlite3.sqlite_backend_initializer import SQLiteBackendInitializer

import unittest


class SQLiteBackendInitializerTest(unittest.TestCase):

    # Shouldn't throw anything
    def test_create_sqlite_db(self):
        self.database = SQLiteBackendInitializer(":memory:")
