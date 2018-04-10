# !/usr/bin/env python3
#
# src/intermediary.py
# Authors:
#     Samuel Vargas
#     Alex Gao

from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from src.interfaces import BackendIO
from src.settings import SETTINGS
from src.api import authentication, election, vote, tally
import uuid

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(authentication)
app.register_blueprint(election)
app.register_blueprint(vote)
app.register_blueprint(tally)

app.config['SECRET_KEY'] = str(uuid.uuid4())
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False


def start(backend_io: BackendIO, shared_password: str = None, url: str = None, port: int = None):
    assert backend_io, "'backend_io' cannot be None"

    SETTINGS['BACKEND_IO'] = backend_io

    if shared_password:
        SETTINGS['SHARED_PASSWORD'] = shared_password

    if url:
        SETTINGS['URL'] = url

    if port:
        SETTINGS['PORT'] = port

    app.run(SETTINGS['URL'], SETTINGS['PORT'])


def start_test(backend_io: BackendIO, shared_password: str = None):
    assert backend_io, "'backend_io' cannot be None"

    SETTINGS['BACKEND_IO'] = backend_io

    if shared_password:
        SETTINGS['SHARED_PASSWORD'] = shared_password

    test_app = app.test_client()
    test_app.testing = True
    return test_app

if __name__ == '__main__':
    app.run(debug=True)
