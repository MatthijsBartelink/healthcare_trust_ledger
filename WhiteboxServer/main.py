from block import Block
import dbinterface

from flask import Flask
import sqlite3 as sl
import requests

from datetime import datetime
from hashlib import sha256

discovery_server = "http://145.100.104.48:5000"
verify_with_count = 7

app = Flask(__name__)

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

@app.route('/trust/<endpoint>')
def trust(endpoint):
    """
    Establish this whitebox as a endorser for endpoint.
    """

    context = dbinterface.getContext()

    if dbinterface.isInLedgers(endpoint):
        #Ledger is locally available, therefore the whitebox already endorses endpoint
        return "Whitebox is already an endorser"
    else:
        request_url = "{}/getnumendorsers/{}".format(discovery_server, endpoint)
        r = requests.get(request_url)
        if r.status_code != 200:
            return "Discovery server error, endorse failed"

        if r.text == "0":
            #entirely new ledger
            msg = setupNewLedger(endpoint)
            request_url = "{}/register/{}&{}".format(discovery_server, context[1], endpoint)
            r = requests.get(request_url)
            if r.status_code == 200:
                if r.text == "now endorsing endpoint " + str(endpoint):
                    print("Registration succeeded, but other registration already exists. Should now discover other endorser, but this is not implemented")
            else:
                print("Registration failed. Should be retried automatically, but this is not implemented")
            return msg
        else:
            #ledger exists elsewhere
            other_endorsers_count = int(r.text)
            references_used = other_endorsers_count
            if references_used > verify_with_count:
                references_used = verify_with_count

            reference = downloadremotereferences(endpoint, 1)[0]

            downloadremoteledger(endpoint, reference)

            if validatestoredledger(endpoint, verify_with_count):
                # make ledgers entry
                with sl.connect('trustledgers.db') as con:
                    con.execute('INSERT INTO LEDGERS (id, name) values(?, ?)', (context[2]+1, endpoint))
                dbinterface.setNumledgers(context[2]+1)

                #TODO: register with other whiteboxes
                #TODO: register with discovery_server
                request_url = "{}/register/{}&{}".format(discovery_server, context[1], endpoint)
                r = requests.get(request_url)
                if r.status_code == 200:
                    return "Trust-link succesfully established"
                else:
                    return "Trust-link establishment succeeded, but discovery server registration failed. Should retry automatically, but this is not implemented"
            else:
                return "Trust-link failed, ledger verification failed"


    return 'trust failed'

@app.route('/downloadledger/<endpoint>')
def downloadledger(endpoint):
    return send_file('./{}.db'.format(endpoint), attachment_filename='{}.db'.format(endpoint))

@app.route('/getlastblockhash/<endpoint>')
def getlastblockhash(endpoint):
    context = dbinterface.getEndpointContext(endpoint)
    if context[1] != endpoint:
        return False
    lastblock = dbinterface.getBlock(context[2])
    return lastblock.compute_hash()

@app.route('/presentblock/<endpoint>&<block>')
def presentblock(endpoint, blockJSON):
    block = dbinterface.blockfromJSON(blockJSON)

    if block.endpoint != endpoint:
        return "block rejected, endpoint doesn't match"
    if block.operation != "ADD" and block.operation != "REV" and block.operation != "SMP":
        return "block rejected, operation unknown"
    # if block.timestamp #TODO: validate timestamp

    dbinterface.getBlock(block.id, endpoint)
    # if block.previous_hash

    #TODO: reject block for other reasons

    #TODO: store block if accepted
    return "block accepted"

def downloadremoteledger(endpoint, reference):
    request_url = '{}/downloadledger/{}'.format(discovery_server, reference)
    r = requests.get(request_url)
    open('{}.db'.format(endpoint), 'wb').write(r.content)

def downloadremotereferences(endpoint, count):
    references = []
    i = 0
    while i < count:
        request_url = '{}/getreference/{}'.format(discovery_server, endpoint)
        r = requests.get(request_url)
        if r.status_code != 200:
            return "Discovery server error, reference get failed"
        reference = r.text
        if reference not in references:
            references.append(reference)
            i += 1
    return references

def validatestoredledger(endpoint, endorsercount):
    context = dbinterface.getEndpointContext(endpoint)
    if context[1] != endpoint:
        return False
    lastblock = dbinterface.getBlock(context[2])
    lasthash = lastblock.compute_hash()

    #TODO: local hash validation

    # Remote validation
    references = downloadremotereferences(endpoint, endorsercount)
    successes = 0
    for reference in references:
        request_url = "{}/getlastblockhash/{}".format(reference, endpoint)
        r = requests.get(request_url)
        if r.text == lasthash:
            successes += 1

    if successes > endorsercount/2:
        return True
    return False



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

    newblock = Block(1, "ADD", timestamp, 1, keyhash, context[1], endpoint)
    dbinterface.addBlock(newblock, endpoint)

    return "new trust link and ledger for {}".format(endpoint)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
