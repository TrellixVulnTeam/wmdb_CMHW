
import random
from datetime import datetime

import requests
from requests import Timeout

from globals import db_connection


def parse_omdb_date(date_string):
    """
    Get a date from a date string as formatted by imdb
    :param date_string: YYYY-MM-DD
    :return: datetime object representing this date
    """
    try:
        # try to parse the date
        date = datetime.strptime(date_string, "%d %b %Y")
        return date
    except ValueError:
        return None


def user_info(given_name):
    """
    Get the user info (u_name and fake email) from a given name. Parses u_name as first_last and email as
    first_last@ymdb.com
    :param given_name: given name for this user
    :return: (u_name, email) from the given name
    """
    stripped = given_name.replace(' ', '_').lower()
    email = stripped + '@ymdb.com'
    return stripped, email


def get_director(director_name):
    """
    Get or create the director user based on name.
    :param director_name: name of director exactly from api
    :return: uid of director
    """
    # get default info from name
    u_name, email = user_info(director_name)
    # check if the user exists
    curs.execute('SELECT UID FROM USER WHERE u_name = ?', (u_name,))
    user_uid = curs.fetchone()
    if user_uid is not None:
        # insert into directors if not already there
        curs.execute('INSERT INTO DIRECTOR SELECT (?, NULL , ?, NULL) \
                     WHERE NOT EXISTS(SELECT UID FROM DIRECTOR WHERE UID == ?)',
                     (user_uid, director_name, user_uid))
        db_connection.commit()
        return user_uid
    else:
        # insert into both user table and director table
        curs.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", (u_name, email))
        user_uid = curs.lastrowid
        curs.execute("INSERT INTO DIRECTOR VALUES (?, NULL, ?, NULL)", (user_uid, director_name))
        db_connection.commit()
        return user_uid


def get_actor(actor_name):
    """
    Get or create the actor user based on name.
    :param actor_name: name of actor exactly from api
    :return: uid of actor
    """
    # get default info from name
    u_name, email = user_info(actor_name)
    # check if the user exists
    curs.execute('SELECT UID FROM USER WHERE u_name = ?', (u_name,))
    user_uid = curs.fetchone()
    if user_uid is not None:
        # insert into actors if not already there
        curs.execute('INSERT INTO ACTOR SELECT (?, NULL , ?, NULL) \
                     WHERE NOT EXISTS(SELECT UID FROM ACTOR WHERE UID == ?)',
                     (user_uid, actor_name, user_uid))
        db_connection.commit()
        return user_uid
    else:
        # insert into both user table and director table
        curs.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", (u_name, email))
        user_uid = curs.lastrowid
        curs.execute("INSERT INTO ACTOR VALUES (?, NULL, ?, NULL)", (user_uid, director_name))
        db_connection.commit()
        return user_uid


# ------------------------- begin script ------------------------- #
with open('api.key', 'r') as key_file:
    api_key = key_file.read().replace('\n', '')

movie_api = 'http://www.omdbapi.com/'

review_text = {'', 'terrible, just terrible.', "worst movie I've ever seen", 'I liked it.', "wasn't great", "amazing!",
               "best movie in the world", "who made this?"}

mid_vals = random.sample(range(1, 3135393), 300000)

curs = db_connection.cursor()

for i in mid_vals:
    try:
        imdb_id = 'tt' + format(i, '07')
        payload = {'i': imdb_id, 'type': 'movie', 'apikey': api_key}
        response = requests.get(movie_api, params=payload, timeout=0.15)
        response.raise_for_status()
        data = response.json()

        # skip bad responses
        if data['Response'] == 'False':
            print('skipped because false response')
            continue
        # skip non movies
        if data['Type'] != 'movie':
            print('skipped because type: ' + data['Type'])
            continue

        # skip movies already entered
        title = data['Title']
        curs.execute("SELECT MID FROM MOVIE WHERE title = ?", (title,))
        mid = curs.fetchone()
        if mid is not None:
            print('skipped because exists: ' + str(mid))
            continue
    except Timeout:
        print('skipped because timeout')
        continue
    except:
        print('other error')
        continue

    try:
        # insert or get director
        director_name = data['Director']
        dir_uid = get_director(director_name)
        # insert the movie
        release_date = parse_omdb_date(data['Released'])
        curs.execute("INSERT INTO MOVIE VALUES (NULL, ?, ?, ?, 1, strftime('%s', 'now'))", (dir_uid, title, release_date))
        db_connection.commit()
        print("added movie: " + title)
        mid = curs.lastrowid
        # get list of actors
        actors = data['Actors'].split(', ')
        for actor in actors:
            act_uid = get_actor(actor)
            curs.execute("INSERT INTO ACTED_IN VALUES (?, ?, 'UNAVAILABLE')", (mid, act_uid))
            print("added actor: " + actor)
            db_connection.commit()
        # insert random ratings
        for review in random.sample(range(1, 5), 6):
            rand_uid = random.ranInt(1, 10000)
            curs.execute("INSERT INTO REVIEW VALUES (?, ?, ?, ?, STRFTIME('%s', 'now'))",
                         (mid, rand_uid, random.choice(review_text), review))
            print("added review: " + str(review))
            db_connection.commit()
    except:
        print('exception')
        db_connection.rollback()
