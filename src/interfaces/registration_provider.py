#!/usr/bin/env python3
#
# src/interfaces/registration_provider
# Authors:
#     Samuel Vargas

import abc


class RegistrationProvider(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def is_user_registered(self, username: str, password: str) -> bool:
        """
        Contacts an external registration server (or uses an internal DB)
        to verify if a user has been registered.
        :param username: The client's username.
        :param password: An plaintext password, you should hash this before
                         sending it / storing it anywhere!
        :return: True if the user has registered previously.
        """
        raise NotImplementedError()
