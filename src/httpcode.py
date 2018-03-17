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

#
# Successful (2xx)
#

# General
SIGNUP_OK = \
    _httpcode("Signup successfully completed.", status.HTTP_201_CREATED)

ELECTION_CREATED_SUCCESSFULLY = \
    _httpcode("Election successfully created.", status.HTTP_201_CREATED)

LOGIN_SUCCESSFUL = \
    _httpcode("Login successful. You are now authenticated.", status.HTTP_200_OK)

#
# Client Errors (4xx)
#

# General
MISSING_OR_MALFORMED_JSON = \
    _httpcode("JSON was not provided or is non parseable", status.HTTP_400_BAD_REQUEST)

MISSING_LOGIN_PARAMETERS = \
    _httpcode("Missing 'username', 'password', or 'account_type'", status.HTTP_400_BAD_REQUEST)

USER_NOT_REGISTERED = \
    _httpcode("Register with the Registration server prior to signing-in", status.HTTP_400_BAD_REQUEST)

USER_ALREADY_AUTHENTICATED = \
    _httpcode("You have aleady logged in. Log out first before logging back in.", status.HTTP_400_BAD_REQUEST)

LOG_IN_FIRST = \
    _httpcode("You are not logged in. Login with /api/login/ first", status.HTTP_403_FORBIDDEN)


# Elections
ELECTION_WITH_TITLE_ALREADY_EXISTS = \
    _httpcode("You cannot create an election with this title because one already exists", status.HTTP_400_BAD_REQUEST)
