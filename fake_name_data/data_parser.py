import csv

import random
import sqlite3

import bcrypt

from globals import db_connection

headers = ['Username', 'EmailAddress', 'GivenName', 'Surname', 'Birthday']
percent_mods = 1
percent_pass = 2

with open('fng_0.csv', 'r') as csv_file:
    curs = db_connection.cursor()
    reader = csv.DictReader(csv_file, fieldnames=headers)
    for entry in reader:
        try:
            # add the user
            curs.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))",
                         (entry['Username'], entry['EmailAddress']))
            uid = curs.lastrowid
            # only give a certain percentage passwords, because it's so expensive to compute
            if random.randint(0, 99) < percent_pass:
                # generate a password of uidLastname (e.g., 5Eichenhofer)
                password = str(uid) + entry['Surname']
                curs.execute("INSERT INTO PASSWORD VALUES (?, ?)", (uid, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())))
            # make some percentage of users a mod
            if random.randint(0, 99) < percent_mods:
                # make this user a moderator
                curs.execute("INSERT INTO ADMIN VALUES (?, 'moderator')", (uid,))
            # commit this addition
            db_connection.commit()
        except sqlite3.IntegrityError:
            # just rollback and ignore
            db_connection.rollback()
