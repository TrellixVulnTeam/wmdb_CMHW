import os
import sqlite3

global db_connection

db_connection = sqlite3.connect(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ym.db'
    )
)
