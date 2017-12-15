import sqlite3

from globals import db_connection
from data_generation import util


def make_poster(mid, filename):
    """
    Enter a poster reference.
    :param mid: movie id for this poster
    :param filename: filename for access to image in static/posters
    """
    curs = db_connection.cursor()
    curs.execute('REPLACE INTO POSTER VALUES (?, ?, ?)', (mid, filename, 1))
    db_connection.commit()


def make_role(mid, uid, character):
    """
    Enter a role into the database.
    :param mid: movie id
    :param uid: actor id
    :param character: character name for this role
    :return: None
    """
    curs = db_connection.cursor()
    curs.execute('INSERT INTO ACTED_IN VALUES (?, ?, ?)', (mid, uid, character))
    db_connection.commit()


def make_review(mid, uid, text, rating):
    """
    Enter a review into the database.
    :param mid: movie id
    :param uid: reviewer id
    :param text: review text
    :param rating: 0-5 rating
    :return: None
    """
    curs = db_connection.cursor()
    curs.execute("INSERT INTO REVIEW VALUES (?, ?, ?, ?, strftime('%s', 'now'))", (mid, uid, text, rating))
    db_connection.commit()


def lookup_movie(movie_title):
    """
    Try to find a movie by title. Return null if not found or MID if found.
    :param movie_title: title of movie
    :return: mid or none
    """
    # get the database cursor
    curs = db_connection.cursor()
    # select movie
    curs.execute('SELECT MID FROM MOVIE WHERE title = ?', (movie_title,))
    rows = curs.fetchone()
    # check if anything returned
    if rows is None:
        # nothing found, return none
        return None
    # otherwise return mid of first row
    return rows[0]


def make_movie(director_uid, title, release_date):
    """
    Insert a new movie into the database.
    :param director_uid: director's user id
    :param title: movie title
    :param release_date: unix time release date
    :return:
    """
    curs = db_connection.cursor()
    curs.execute("INSERT INTO MOVIE VALUES (NULL, ?, ?, ?, 1, strftime('%s', 'now'))",
                 (director_uid, title, release_date))
    db_connection.commit()
    return curs.lastrowid


def lookup_user(full_name):
    """
    Try to find the given user in the USER table based on default info generator (in util.py) users user id to do lookup
    :param full_name: full name of director
    :return: uid or None
    """
    # get the database cursor
    curs = db_connection.cursor()
    # get u_name and email
    u_name, email = util.user_info(full_name)
    # select user
    curs.execute('SELECT UID FROM USER WHERE u_name = ?', (u_name,))
    rows = curs.fetchone()
    # check if anything returned
    if rows is None:
        # nothing found, return none
        return None
    # otherwise return uid of first row
    return rows[0]


def make_user(full_name):
    """
    Enter a new user into the database given full name.
    :param full_name: user's full name
    :return: uid of newly created user
    """
    curs = db_connection.cursor()
    # insert into database
    curs.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", util.user_info(full_name))
    db_connection.commit()
    # get the mid
    return curs.lastrowid


def get_director_dob(dir_uid):
    """
    Try to find the director in the director table. Return true or false.
    :param dir_uid: uid for the potential director
    :return: dob if present or false if not
    """
    curs = db_connection.cursor()
    curs.execute('SELECT UID, DoB FROM DIRECTOR WHERE UID = ?', (dir_uid,))
    rows = curs.fetchone()
    if rows is not None:
        return rows[1]
    return False


def make_director(dir_uid, dir_name, dob):
    """
    Create a director entry with given uid and dob. famous for mid is null
    :param dir_uid: director uid
    :param dob: director date of birth (in unix time)
    :return: None
    """
    curs = db_connection.cursor()
    curs.execute('INSERT INTO DIRECTOR VALUES (?, NULL, ?, ?)', (dir_uid, dir_name, dob))
    db_connection.commit()


def get_actor_dob(act_uid):
    """
    Check to see if uid is in actor table, if so return true, otherwise false
    :param act_uid: uid to search
    :return: dob if present or false if not
    """
    curs = db_connection.cursor()
    curs.execute('SELECT UID, DoB FROM ACTOR WHERE UID = ?', (act_uid,))
    rows = curs.fetchone()
    if rows is not None:
        return rows[1]
    return False


def make_actor(act_uid, actor_name, dob):
    """
    Insert a new actor into the actor table
    :param act_uid: uid for new actor
    :param actor_name: name of actor
    :param dob: date of birth in unix time
    :return: None
    """
    curs = db_connection.cursor()
    curs.execute('INSERT INTO ACTOR VALUES (?, NULL, ?, ?)', (act_uid, actor_name, dob))
    db_connection.commit()
