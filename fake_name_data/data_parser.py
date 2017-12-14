import csv
import time
import random
import sqlite3

import bcrypt

from globals import db_connection

headers = ['Username', 'EmailAddress', 'GivenName', 'Surname', 'Birthday']
percent_mods = 10
percent_pass = 100

total_processed = 0
total_skipped = 0
start_time = time.time()

with open('fng_0.csv', 'r') as csv_file:
    curs = db_connection.cursor()
    reader = csv.DictReader(csv_file, fieldnames=headers)
    for entry in reader:
        total_processed = total_processed + 1
        try:
            # generate better username to avoid collision
            u_name = entry['GivenName'] + '.' + entry['Surname'] + entry['Birthday'].split('/')[2]
            email = u_name + '@ymdb.com'
            # add the user
            curs.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", (u_name, email))
            uid = curs.lastrowid
            # generate a password of uidLastname (e.g., 5Eichenhofer)
            password = str(uid) + entry['Surname']
            curs.execute("INSERT INTO PASSWORD VALUES (?, ?)",
                         (uid, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())))
            # make some percentage of users a mod
            if random.randint(0, 99) < percent_mods:
                # make this user a moderator
                curs.execute("INSERT INTO ADMIN VALUES (?, 'moderator')", (uid,))
            # commit this addition
            db_connection.commit()
        except sqlite3.IntegrityError:
            # just rollback and ignore
            print('skipped')
            total_skipped = total_skipped + 1
            db_connection.rollback()

        # don't need 100000 anymore
        if total_processed > 999:
            break

end_time = time.time()

print('total processed: ' + str(total_processed))
print('total skipped: ' + str(total_skipped))
print('total time (seconds): ' + str(end_time - start_time))
