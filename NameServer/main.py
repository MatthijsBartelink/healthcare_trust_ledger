import secrets

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
    # print("received registration:\nendorser: " + myaddress + " endpoint: " + endpoint)

    # Omitted in this prototype: Verify that myaddress is a valid whitebox and actual sender

    if dbinterface.knownEndpoint(endpoint):
        if dbinterface.knownEndorser(endpoint, myaddress):
            return "Registration failed, already registered"
        con = sl.connect(str(endpoint)+'.db')
        con.execute("INSERT INTO ENDORSER (id, address) values (?, ?)", (dbinterface.findEndorserCount(endpoint), myaddress))
        con.commit()
        dbinterface.incEndorserCount(endpoint)
        return "now endorsing endpoint " + str(endpoint)
    else:
        dbinterface.addToLedgers(endpoint)
        #make db for endpoint
        con = sl.connect(str(endpoint)+'.db')
        con.execute("""
            CREATE TABLE ENDORSER (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                address TEXT
            );
        """)
        con.execute("INSERT INTO ENDORSER (id, address) values (?, ?)", (dbinterface.findEndorserCount(endpoint), myaddress))
        con.commit()
        dbinterface.incEndorserCount(endpoint)
        return "Registered new endpoint"

@app.route('/deregister/<myaddress>/<endpoint>')
def deregister(myaddress, endpoint):
    # Omitted in this prototype: Verify that myaddress is a valid whitebox and actual sender
    if dbinterface.knownEndpoint(endpoint):
        if dbinterface.knownEndorser(endpoint, myaddress):
            dbinterface.deleteEndorser(endpoint, myaddress)
            dbinterface.decEndorserCount(endpoint)
            return "Deregistration succeeded"
        else:
            return "Deregistration failed, endorser not known"
    else:
        return "Deregistration failed, endpoint not known"

@app.route('/getnumendorsers/<endpoint>')
def getnumendorsers(endpoint):
    if dbinterface.knownEndpoint(endpoint):
        return str(dbinterface.findEndorserCount(endpoint))
    return "0"

@app.route('/getreference/<endpoint>')
def getreference(endpoint):
    if dbinterface.knownEndpoint(endpoint):
        num_endorsers = dbinterface.findEndorserCount(endpoint)
        if num_endorsers == 0:
            return "no endorsers"
        else:
            random_reference = secrets.randbelow(num_endorsers)
            endorser = dbinterface.getEndorserById(endpoint, random_reference)
            return endorser[1]
    else:
        return "endpoint not known"

if __name__ == '__main__':
    app.run(host="0.0.0.0")
