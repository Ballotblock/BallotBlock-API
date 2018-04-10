#
#  src/api/authentication.py
#  Authors:
#       Samuel Vargas
#

from flask import Blueprint, request
from src.authentication_cookie import AuthenticationCookie
from src import httpcode
from src.settings import SETTINGS

authentication = Blueprint("authentication", __name__)


@authentication.route("/api/authentication", methods=["POST"])
def cookie_has_valid_authentication():
    # Verify the user's provided authentication cookie.
    if not AuthenticationCookie.is_encrypted_by_registration_server(SETTINGS["SHARED_PASSWORD"], request.cookies):
        return httpcode.MISSING_OR_MALFORMED_AUTHENTICATION_COOKIE

    return httpcode.VALID_AUTHENTICATION_COOKIE
