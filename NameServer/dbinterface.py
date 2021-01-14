"""
This file contains simple getters and setters for database interaction. Any
repeated SQL query should be implemented here.
"""

import sqlite3 as sl

def knownEndpoint(endpoint):
    with sl.connect('whichledgers.db') as con:
        data = con.execute("SELECT * FROM LEDGER WHERE name = ?", (endpoint, ))
        for line in data:
            if line[1] == endpoint:
                return True
    return False

def knownEndorser(endpoint, address):
    with sl.connect(str(endpoint)+'.db') as con:
        data = con.execute("SELECT * FROM ENDORSER WHERE address = ?", (address, ))
        for line in data:
            print("comparing " + str(line[1]) + " with " + str(address))
            if str(line[1]) == str(address):
                return True
    return False

def deleteEndorser(endpoint, address):
    with sl.connect(str(endpoint)+'.db') as con:
        con.execute("DELETE FROM ENDORSER WHERE address=?", (address, ))

def addToLedgers(endpoint):
    with sl.connect('whichledgers.db') as con:
        con.execute("INSERT INTO LEDGER (name, count) values (?, ?)", (endpoint, 0))

def findEndorserCount(endpoint):
    with sl.connect('whichledgers.db') as con:
        data = con.execute("SELECT * FROM LEDGER WHERE name = ?", (endpoint, ))
        for line in data:
            return line[2]

def incEndorserCount(endpoint):
    endorsercount = findEndorserCount(endpoint)
    with sl.connect('whichledgers.db') as con:
        data = con.execute("UPDATE LEDGER SET count = ? WHERE name = ?", (endorsercount + 1, endpoint))

def decEndorserCount(endpoint):
    endorsercount = findEndorserCount(endpoint)
    with sl.connect('whichledgers.db') as con:
        data = con.execute("UPDATE LEDGER SET count = ? WHERE name = ?", (endorsercount - 1, endpoint))

def getEndorserById(endpoint, id):
    with sl.connect(str(endpoint)+'.db') as con:
        data = con.execute("SELECT * FROM ENDORSER WHERE id = ?", (id, ))
        for line in data:
            return line
