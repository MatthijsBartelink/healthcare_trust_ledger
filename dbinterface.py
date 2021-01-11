"""
This file contains simple getters and setters for database interaction. Any
repeated SQL query should be implemented here.
"""

def getContext():
    context = ""
    data = con.execute("SELECT * FROM ENVIRONMENT WHERE id = 1")
    for line in data:
        context = line
    return context

# def updatecontext(name, num_ledgers):
#     with con:
#         con.execute("UPDATE ENVIRONMENT SET name = ? , num_ledgers = ? WHERE id = ?", (name, num_ledgers, 1))

def setName(name):
    con.execute("UPDATE ENVIRONMENT SET name = ? WHERE id = ?", (name, 1))

def setNumledgers(num_ledgers):
    con.execute("UPDATE ENVIRONMENT SET num_ledgers = ? WHERE id = ?", (num_ledgers, 1))

def addBlock(block, endpoint):
    ledgerdata = ""
    data = con.execute("SELECT * FROM LEDGERS WHERE name = ?", endpoint)
    for line in data:
        ledgerdata = line
    con.execute('INSERT INTO ? (id, name, num_ledgers) values(?, ?, ?)', (endpoint, name, ledgerdata[2] + 1))
    con.execute("UPDATE LEDGERS SET length = ? WHERE name = ?", (ledgerdata[2] + 1, endpoint))
