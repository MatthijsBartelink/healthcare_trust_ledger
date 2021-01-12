"""
This file contains simple getters and setters for database interaction. Any
repeated SQL query should be implemented here.
"""

import sqlite3 as sl

def knownEndpoint(endpoint):
    with sl.connect('whichledgers.db') as con:
        data = con.execute("SELECT * FROM LEDGERS WHERE name = ?", endpoint)
        for line in data:
            if line[1] == endpoint:
                return True
    return False

def addToLedgers(endpoint):
    with sl.connect('whichledgers.db') as con:
        con.execute("INSERT INTO LEDGERS (name) values (?)", (endpoint, ))
    
