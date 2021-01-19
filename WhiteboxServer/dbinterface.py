"""
This file contains simple getters and setters for database interaction. Any
repeated SQL query should be implemented here.
"""
import sqlite3 as sl
import JSON
from block import Block

def getContext():
    context = ""
    with sl.connect('trustledgers.db') as con:
        data = con.execute("SELECT * FROM ENVIRONMENT WHERE id = 1")
        for line in data:
            context = line
    return context

# def updatecontext(name, num_ledgers):
#     with con:
#         con.execute("UPDATE ENVIRONMENT SET name = ? , num_ledgers = ? WHERE id = ?", (name, num_ledgers, 1))

def setName(name):
    with sl.connect('trustledgers.db') as con:
        con.execute("UPDATE ENVIRONMENT SET name = ? WHERE id = ?", (name, 1))

def setNumledgers(num_ledgers):
    with sl.connect('trustledgers.db') as con:
        con.execute("UPDATE ENVIRONMENT SET num_ledgers = ? WHERE id = ?", (num_ledgers, 1))

def getEndpointContext(endpoint):
    context = ""
    with sl.connect(str(endpoint)+".db") as con:
        data = con.execute("SELECT * FROM CONTEXT WHERE id = 1")
        for line in data:
            context = line
    return context

def addBlock(block, endpoint):

    context = getEndpointContext(endpoint)

    with sl.connect(str(endpoint)+".db") as con:
        # increment length of blockchain by one
        con.execute("UPDATE CONTEXT SET length = ? WHERE id = 1", (context[2]+1, ))
        # add block to db
        con.execute("INSERT INTO BLOCK (id, block_json) values (?, ?)", (context[2]+1, block.toJSON()))

def getBlock(id, endpoint):
    with sl.connect(str(endpoint)+".db") as con:
        data = con.execute("SELECT * FROM BLOCK WHERE id = ?", (id, ))
        for line in data:
            return blockfromJSON(line[1])

def isInLedgers(endpoint):
    with sl.connect('trustledgers.db') as con:
        data = con.execute('SELECT * FROM LEDGERS WHERE name=?', (endpoint, ))
        for line in data:
            if line[1] == endpoint:
                return True

    return False

def blockfromJSON(blockJSON):
    dictversion = JSON.loads(blockJSON)
    return block(dictversion['index'], dictversion['operation'], dictversion['timestamp'], dictversion['logicaltimestamp'],
                 dictversion['previous_hash'], dictversion['endorser'], dictversion['endpoint'],
                 dictversion['nonce'], dictversion['positive'])
