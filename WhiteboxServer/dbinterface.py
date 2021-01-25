"""
This file contains simple getters and setters for database interaction. Any
repeated SQL query should be implemented here.
"""
import sqlite3 as sl
import json
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
        if block.index == context[2]+1:
            con.execute("UPDATE CONTEXT SET length = ? WHERE id = 1", (context[2]+1, ))
        # add block to db
            con.execute("INSERT INTO BLOCK (id, block_json) values (?, ?)", (context[2]+1, block.toJSON()))
    performblockoperation(block)

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
    print("JSON RECEIVED:")
    print(blockJSON)
    dictversion = json.loads(blockJSON)
    return Block(dictversion['index'], dictversion['operation'], dictversion['timestamp'], dictversion['logicaltimestamp'],
                 dictversion['previous_hash'], dictversion['endorser'], dictversion['endpoint'],
                 dictversion['nonce'], dictversion['positive'])

def getcompleteledger(endpoint):
    with sl.connect(str(endpoint)+".db") as con:
        data = con.execute('SELECT * FROM LEDGERENTRY ORDER BY id ASC')
        entrylist = []
        for line in data:
            entrylist.append(line)
        return entrylist

def getallblocks(endpoint):
    with sl.connect(str(endpoint)+".db") as con:
        data = con.execute('SELECT * FROM BLOCK ORDER BY id ASC')
        blocklist = []
        for line in data:
            blocklist.append(blockfromJSON(line[1]))
        return blocklist

def performblockoperation(block):
    if block.operation == "ADD" :
        positivenum = 0
        if block.positive:
            positivenum = 1
        with sl.connect(str(block.endpoint)+".db") as con:
            con.execute("INSERT INTO LEDGERENTRY (whitebox, positive, block_id) values(?, ?, ?)", (block.endorser, positivenum, block.index))
    elif block.operation == "REV":
        with sl.connect(str(block.endpoint)+".db") as con:
            con.execute("DELETE FROM LEDGERENTRY WHERE whitebox = ?", (block.endorser, ))
    elif block.operation != "SMP":
        print("block with simplification operation. Currently not implemented")
    else:
        print("Block with unrecognized operation. Something has gone very wrong.")


def deleteLedgerEntry(endpoint):
    context = getcontext()
    with sl.connect('trustledgers.db') as con:
        con.execute('DELETE FROM LEDGERS WHERE name=?', (endpoint, ))
        con.execute("UPDATE ENVIRONMENT SET num_ledgers = ? WHERE id = ?", (context[2] - 1, 1))
