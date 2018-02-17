#!/usr/bin/env python3
#
# src/httpcode.py
# Authors:
#     Samuel Vargas
#

from typing import NamedTuple
from collections import namedtuple
from flask_api import status

HttpCode = NamedTuple("httpcode", [("message", str), ("code", int)])
_httpcode = namedtuple("httpcode", ("message", "code"))

# Successful (2xx)
SIGNUP_OK = \
    _httpcode("Signup successfully completed.", status.HTTP_201_CREATED)

ELECTION_CREATED_SUCCESSFULLY = \
    _httpcode("Election successfully created.", status.HTTP_201_CREATED)

# Client Errors (4xx)
MISSING_OR_MALFORMED_JSON = \
    _httpcode("JSON was not provided or is non parseable", status.HTTP_400_BAD_REQUEST)

LOG_IN_FIRST = \
    _httpcode("You are not logged in. Login with /api/login/ first", status.HTTP_403_FORBIDDEN)
