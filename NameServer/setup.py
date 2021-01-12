"""
Setup for the db. Should be run only once, before ever starting the server.
"""
import sqlite3 as sl

con = sl.connect('whichledgers.db')
name = "testname1"

with con:
    # make ledgers table
    con.execute("""
        CREATE TABLE LEDGERS (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
    """)
    # make environment variables storage area
    # con.execute("""
    #     CREATE TABLE ENVIRONMENT (
    #         id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    #         name TEXT,
    #         num_ledgers INTEGER
    #     )
    # """)
    # con.execute('INSERT INTO ENVIRONMENT (id, name, num_ledgers) values(?, ?, ?)', (1, name, 0))
