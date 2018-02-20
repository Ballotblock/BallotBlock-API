#
# src/registration_server_provider.py
# Authors:
#     Samuel Vargas

from src.interfaces.registration_provider import RegistrationProvider


class RegistrationServerProvider(RegistrationProvider):
    def is_user_registered(self, username: str, password: str) -> bool:
        raise NotImplementedError("")
