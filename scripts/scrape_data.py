from datetime import datetime

import requests
import bs4

from db_connection import db_connection

MOVIE_URL = 'http://www.imdb.com/title/'
ACTOR_URL = 'http://www.imdb.com/name/'


def unix_time(dt):
    """
    Covert datetime object to seconds to/from epoch
    :param dt: datetime object to convert
    :return: seconds from epoch (unix time), may be positive or negative
    """
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds()


def parse_movie(movie_id):
    """
    Put movie data into database based on movie ID.
    :param movie_id: imdb id for this movie
    """
    # get a database cursor
    curs = db_connection.cursor()
    # get page
    res = requests.get(MOVIE_URL + movie_id)
    res.raise_for_status()
    page = bs4.BeautifulSoup(res.text, 'html.parser')
    # get title
    title = page.find('h1', itemprop='name').contents[0].strip(u"\u00A0")
    # get release date
    release = parse_date(page.find('meta', itemprop='datePublished')['content'])
    # create and/or lookup director
    dir_uid = get_director_uid(page)
    # enter the movie into the database
    curs.execute("INSERT INTO MOVIE VALUES (NULL, ?, ?, ?, 0, strftime('%s', 'now'))",
                 (dir_uid, title, unix_time(release)))
    # commit the changes
    db_connection.commit()


def get_director_uid(page):
    """
    Create or find the director from a given imdb movie page. Insert into director and user table if necessary. Get the
    UID of the director and return it.
    :param page: IMDB movie page
    :return: director UID
    """
    # get a database cursor
    curs = db_connection.cursor()
    try:
        # get director id
        dir_imdb_id, dir_name = get_director_info(page.find('span', itemprop='director'))
        # get the date of birth for the director
        dir_dob = get_dob(dir_imdb_id)
        # check if the director
        curs.execute('SELECT UID FROM DIRECTOR WHERE given_name = ?', (dir_name,))
        dir_uid = curs.fetchone()
        if dir_uid is None:
            # if no director is found, check if this director is already entered as an actor
            curs.execute('SELECT UID FROM ACTOR WHERE given_name = ?', (dir_name,))
            dir_uid = curs.fetchone()
        if dir_uid is None:
            # if not in director or actor, must add new user/director
            curs.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", user_info(dir_name))
            dir_uid = curs.lastrowid
        # add the new (or found) user to the director table
        curs.execute('INSERT INTO DIRECTOR VALUES (?, NULL, ?, ?)', (dir_uid, dir_name, dir_dob))
        # commit the changes
        db_connection.commit()
        # return the uid of the director
        return dir_uid
    except RuntimeError as err:
        # any error should rollback changes
        db_connection.rollback()
        raise err


def get_dob(name_id):
    """
    Get an actor date of birth from an id.
    :param name_id: imdb id for this actor
    :return: date of birth for actor
    """
    res = requests.get(ACTOR_URL + name_id)
    res.raise_for_status()
    page = bs4.BeautifulSoup(res.text, 'html.parser')
    dob = page.find('time', itemprop='birthDate')['datetime']
    return parse_date(dob)


def get_director_info(director_span):
    """
    Get the director information from the imdb span tag
    :param director_span: span tag contents as taken from page.find('span' ...)
    :return: {dir_id : imdb director id, dir_name : director name}
    """
    # get the url to the director and split it by directory separator
    split_url_path = director_span.find('a', itemprop='url')['href'].split('/')
    # the second element contains {{id}}?ref, so split again by '?' char
    dir_id = split_url_path[2].split('?')[0]
    # name is in the span with prop "name"
    name = director_span.find('span', itemprop='name').contents[0]
    return str(dir_id), str(name)


def parse_date(date_string):
    """
    Get a date from a date string as formatted by imdb
    :param date_string: YYYY-MM-DD
    :return: datetime object representing this date
    """
    return datetime.strptime(date_string, "%Y-%m-%d")


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


# ----------------------------------- start script ----------------------------------- #
parse_movie('tt0111161')
