from flask import Flask
app = Flask(__name__)


"""
Change the line below to switch to sqllite backend
Below is the line to change it to: 
from .intermediary import * 
"""
from src import hyperledger_intermediary