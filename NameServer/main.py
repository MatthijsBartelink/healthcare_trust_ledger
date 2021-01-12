from flask import Flask
import sqlite3 as sl

import dbinterface

app = Flask(__name__)

@app.route('/')
def index():
    """
    Index page for the name server. There is no use for this page.
    """
    return 'Index Page, not used'

@app.route('/register/<myaddress>/<endpoint>')
def register(myaddress, endpoint):
    """
    Register myaddress as an endorser for endpoint.
    """
    # Omitted in this prototype: Verify that myaddress is a valid whitebox and actual sender

    if dbinterface.knownEndpoint(endpoint):

    else:
        dbinterface.addToLedgers(endpoint)
        #make db for endpoint
        con = sl.connect(str(endpoint)+'.db')
        con.execute("")

    return
