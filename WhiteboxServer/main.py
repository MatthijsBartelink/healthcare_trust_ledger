from block import Block
import dbinterface

from flask import Flask, send_file
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
            request_url = "{}/register@{}&{}".format(discovery_server, context[1], endpoint)
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

            if validatestoredledger(endpoint, references_used):
                # make ledgers entry
                with sl.connect('trustledgers.db') as con:
                    con.execute('INSERT INTO LEDGERS (id, name) values(?, ?)', (context[2]+1, endpoint))
                dbinterface.setNumledgers(context[2]+1)

                #TODO: register with other whiteboxes

                #make registration block
                prev_block_hash = dbinterface.getBlock(context[1]-1, endpoint).compute_hash()
                my_registration_block = Block(1, "ADD", datetime.now(), 1, prev_block_hash, context[1], endpoint)

                # add block to own ledger
                dbinterface.addBlock(newblock, endpoint)

                if not pushblocktopeers(endpoint, my_registration_block):
                    return "Trust-link failed, coulnd't establish with peers. Should be retried later automatically, but this is not implemented"

                # register with discovery_server
                request_url = "{}/register@{}&{}".format(discovery_server, context[1], endpoint)
                r = requests.get(request_url)
                if r.status_code == 200:
                    return "Trust-link succesfully established"
                else:
                    return "Trust-link establishment succeeded, but discovery server registration failed. Should retry automatically, but this is not implemented"
            else:
                return "Trust-link failed, ledger verification failed"


    return 'trust failed'

def pushblocktopeers(endpoint, block, tries):
    """
    Push a block to all peers for a given endpoint.
    """
    myaddress = dbinterface.getContext()[1]
    peerlist = dbinterface.getcompleteledger(endpoint)
    totalpeernumber = len(peerlist)

    for i in range(tries):
        retrylist = []
        for peer in peerlist:
            if peer[1] == myaddress:
                continue
            request_url = "http://{}/presentblock/{}&{}".format(peer[1], endpoint, my_registration_block.toJSON())
            r = requests.get(request_url)
            if r.status_code != 200 or r.text != "block accepted":
                retrylist.append(peer)
                #TODO: handle rejection for different reasons differently.
                # send previous block for hash mismatch. insist for time if certain

    if len(retrylist) != 0:
        print("block push failed to {} peers".format(len(retrylist)))

    if len(retrylist) > totalpeernumber * 0.5:
        print("Push failed to {} peers. Block revocation should now be send, but this is not implemented".format(len(retrylist)))
        return False
    else:
        return True


@app.route('/downloadledger/<endpoint>')
def downloadledger(endpoint):
    return send_file('./{}.db'.format(endpoint), attachment_filename='{}.db'.format(endpoint))

@app.route('/getlastblockhash/<endpoint>')
def getlastblockhash(endpoint):
    context = dbinterface.getEndpointContext(endpoint)
    if context[1] != endpoint:
        return False
    lastblock = dbinterface.getBlock(context[2], endpoint)
    return lastblock.compute_hash()

@app.route('/presentblock/<endpoint>&<block>')
def presentblock(endpoint, blockJSON):
    block = dbinterface.blockfromJSON(blockJSON)
    timedelta = datetime.timedelta(minutes=30)
    context = getEndpointContext(block.endpoint)

    # We should check if the message came from the endorser. If not, we should
    # check with the endorser in the block. This is not implemented due to time
    # constraints.

    # TODO: check if endpoint is known
    if block.endpoint != endpoint:
        return "block rejected, endpoint doesn't match"
    if block.index > context[2] + 1:
        return "block rejected, lacking previous blocks"
    if block.operation != "ADD" and block.operation != "REV" and block.operation != "SMP":
        return "block rejected, operation unknown"
    if (datetime.now - timedelta > datetime.fromtimestamp(block.timestamp) or
        datetime.now + timedelta <  datetime.fromtimestamp(block.timestamp)):
        return "block rejected, timestamp off"
    if block.previous_hash != dbinterface.getblock(block.index - 1, endpoint):
        return "block rejected, hash mismatch"
    #TODO: reject block for other reasons

    #TODO: Drop blocks that may now be invalid, or reject block for stored block with precedent

    #TODO: store block if accepted
    if block.index == context[2]+1:
        dbinterface.addBlock(block, endpoint)
        return "block accepted"
    else:
        #TODO: compare block with stored block for timestamp, find correct chain,
        # reject other chain.
        return "block accepted, but not stored(implementation)"

def downloadremoteledger(endpoint, reference):
    request_url = 'http://{}/downloadledger/{}'.format(reference, endpoint)
    r = requests.get(request_url)
    if r.status_code == 200:
        open('{}.db'.format(endpoint), 'wb').write(r.content)
    else:
        print("ledger download failed. Operation should now stop, but this is not implemented")

def downloadremotereferences(endpoint, count):
    references = []
    i = 0
    print("in while loop, count = {}".format(count))
    while i < count:
        request_url = '{}/getreference/{}'.format(discovery_server, endpoint)
        r = requests.get(request_url)
        if r.status_code != 200:
            return "Discovery server error, reference get failed"
        reference = r.text
        if reference not in references:
            references.append(reference)
            i += 1
    print("leaves while loop")
    return references

def validatestoredledger(endpoint, endorsercount):
    context = dbinterface.getEndpointContext(endpoint)
    if context[1] != endpoint:
        return False
    lastblock = dbinterface.getBlock(context[2], endpoint)
    lasthash = lastblock.compute_hash()

    #TODO: local hash validation

    # Remote validation
    references = downloadremotereferences(endpoint, endorsercount)
    successes = 0
    for reference in references:
        request_url = "http://{}/getlastblockhash/{}".format(reference, endpoint)
        r = requests.get(request_url)
        print("received hash: {} my hash: {}".format(r.text, lasthash))
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
        con.execute("""
            CREATE TABLE LEDGERENTRY (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                whitebox TEXT,
                positive INTEGER,
                block_id INTEGER
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
