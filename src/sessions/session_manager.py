#!/usr/bin/env python3
#
# src/interfaces/server_session.py
# Authors:
#     Samuel Vargas

from flask import Session
from enum import Enum, unique


@unique
class AccountType(Enum):
    Voter = 1
    ElectionCreator = 2


class SessionManager:
    @staticmethod
    def login(username: str, account_type: AccountType, session: Session):
        session['username'] = username
        session['account_type'] = account_type

    @staticmethod
    def get_username(session):
        assert SessionManager.is_logged_in(session)
        return session['username']

    @staticmethod
    def logout(username: str, session: Session):
        assert SessionManager.is_logged_in(session)
        session.pop(username, None)

    @staticmethod
    def is_logged_in(session: Session) -> bool:
        return 'username' in session and 'account_type' in session

    @staticmethod
    def voter_is_logged_in(session: Session) -> bool:
        return SessionManager.is_logged_in(session) \
               and session['account_type'] == AccountType.Voter

    @staticmethod
    def election_creator_is_logged_in(session: Session) -> bool:
        return SessionManager.is_logged_in(session) \
               and session['account_type'] == AccountType.ElectionCreator

