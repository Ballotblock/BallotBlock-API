#!/usr/bin/env python3
#
# test/time_manager.py
# Authors:
#   Samuel Vargas
#

import time


class TimeManager:
    @staticmethod
    def election_in_progress(end_date_seconds_timestamp: int):
        return int(time.time()) < end_date_seconds_timestamp
