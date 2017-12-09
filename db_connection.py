import sqlite3
import os


def get_db_connection(disable_autocommit):
    # get the connection to the database file
    db_connection = sqlite3.connect(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'ym.db'
        )
    )
    # enable foreign key on all connections
    db_connection.execute('PRAGMA foreign_keys = ON')
    # setting isolation level to none allows us to handle transactions/rollbacks
    if disable_autocommit:
        db_connection.isolation_level = None
    # return the connection
    return db_connection
