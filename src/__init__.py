

"""
Change the lines below to switch to sqllite backend
Below is the line to change it to, deletate all 3 lines. 

from .intermediary import * 

"""
from flask import Flask
app = Flask(__name__)
from src import hyperledger_intermediary