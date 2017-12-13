import sqlite3

from globals import db_connection
from scripts import util
from scripts.util import user_info


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
    :return: dob if present or None
    """
    curs = db_connection.cursor()
    curs.execute('SELECT UID, DoB FROM DIRECTOR WHERE UID = ?', (dir_uid,))
    rows = curs.fetchone()
    if rows is not None:
        return rows[1]
    return None


def make_director(dir_uid, dir_name, dob):
    """
    Create a director entry with given uid and dob. famous for mid is null
    :param dir_uid: director uid
    :param dob: director date of birth (in unix time)
    :return: None
    """
    curs = db_connection.cursor()
    curs.execute('INSERT INTO DIRECTOR VALUES (?, NULL, ?, ?)', (dir_uid, dir_name, dob))


def get_actor_dob(act_uid):
    """
    Check to see if uid is in actor table, if so return true, otherwise false
    :param act_uid: uid to search
    :return: dob if present or none if not
    """
    curs = db_connection.cursor()
    curs.execute('SELECT UID, DoB FROM ACTOR WHERE UID = ?', (act_uid,))
    rows = curs.fetchone()
    if rows is not None:
        return rows[1]
    return None


def get_director(director_name):
    # get a database cursor
    curs = db_connection.cursor()
    # uid for director
    uid = make_uid(director_name)
    # insert into director (replacing if already there)
    curs.execute('REPLACE INTO DIRECTOR VALUES (?, NULL, ?, NULL)', (uid, director_name))
    # commit change and return uid
    db_connection.commit()
    return uid


def get_actor(actor_name):
    # get a database cursor
    curs = db_connection.cursor()
    # uid for actor
    uid = make_uid(actor_name)
    # insert into actor (replacing if already there)
    curs.execute('REPLACE INTO ACTOR VALUES (?, NULL, ?, NULL)', (uid, actor_name))
    # commit changes and return uid
    db_connection.commit()
    return uid


def make_uid(user_fullname):
    # get default info from name
    u_name, email = user_info(user_fullname)
    # get cursor for lookup
    curs = db_connection.cursor()
    # check if the user exists
    curs.execute('SELECT UID FROM USER WHERE u_name = ?', (u_name,))
    user_uid = curs.fetchone()
    if user_uid is not None:
        # user exists, return uid
        return user_uid[0]
    else:
        # user doesn't exist, create it
        curs.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", (u_name, email))
        user_uid = curs.lastrowid
        # commit change and return uid
        db_connection.commit()
        return user_uid
