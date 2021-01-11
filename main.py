from block import Block
import dbinterface

from flask import Flask
import sqlite3 as sl
from datetime import datetime

app = Flask(__name__)
con = sl.connect('trustledgers.db')

endorsed_key = "This is a replacement for an actual key. Theoretically, any text could be guaranteed this way"

@app.route('/')
def index():
    """
    Index page for the web server. There is no use for this page.
    """
    return 'Index Page, not used'

@app.route('/check/<endpoint>')
def check(endpoint):
    """
    Check to see if this whitebox is an endorser for endpoint. Returns metrics
    describing the trustworthyness of the endpoint.
    """
    return 'Not yet implemented'

@app.route('/endorse/<endpoint>')
def trust(endpoint):
    """
    Establish this whitebox as a endorser for endpoint.
    """
    newLedger = True #TODO: handle ledger which exists elsewhere

    if newLedger:
        setupNewLedger(endpoint)
        return

    return 'Not yet implemented'


def setupNewLedger(endpoint):
    with conn:
        context = dbinterface.getContext()
        # make ledgers entry
        con.execute('INSERT INTO LEDGERS (id, name, length) values(?, ?, ?)', (context[2]+1, endpoint, 0))
        # make table for blocks
        con.execute("""
            CREATE TABLE ? (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                block_json TEXT
            )
        """, endpoint)

        dbinterface.setNumledgers(context[2]+1)

        #make first block
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        keyhash = sha256(endorsed_key.encode()).hexdigest()

        newblock = Block(1, timestamp, 1, keyhash, context[1], endpoint)
        dbinterface.addBlock(newblock, endpoint)
