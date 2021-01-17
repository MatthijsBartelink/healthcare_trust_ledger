from block import Block
import dbinterface

from flask import Flask
import sqlite3 as sl
import requests

from datetime import datetime
from hashlib import sha256

app = Flask(__name__)

endorsed_key = "This is a replacement for an actual key. Theoretically, any text could be guaranteed this way"

if __name__ == '__main__':
    app.run(host="0.0.0.0")

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

    if dbinterface.isInLedgers(endpoint):
        #Ledger is locally available, therefore the whitebox already endorses endpoint
        return "Whitebox is already an endorser"
    else:
        #TODO: handle ledger which exists elsewhere
        msg = setupNewLedger(endpoint)
        # TODO: register new ledger  with nameserver
        return msg

    return 'Not yet implemented'


def setupNewLedger(endpoint):
    """Creates a new ledger where none yet exist, remote or local."""
    context = dbinterface.getContext()
    # make ledgers entry
    with sl.connect('trustledgers.db') as con:
        con.execute('INSERT INTO LEDGERS (id, name) values(?, ?)', (context[2]+1, endpoint))
    # make db for new ledger
    with sl.connect(str(endpoint)+".db") as con:
        con.execute("""
            CREATE TABLE BLOCK (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                block_json TEXT
            )
        """)
        con.execute("""
            CREATE TABLE CONTEXT (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT,
                length INTEGER,
                key TEXT
            )
        """)
        con.execute("INSERT INTO CONTEXT (id, endpoint, length, key) values(?, ?, ?, ?)", (1, endpoint, 0, endorsed_key))

    dbinterface.setNumledgers(context[2]+1)

    #make first block
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    keyhash = sha256(endorsed_key.encode()).hexdigest()

    newblock = Block(1, timestamp, 1, keyhash, context[1], endpoint)
    dbinterface.addBlock(newblock, endpoint)

    return "new trust link and ledger for {}".format(endpoint)
