from datetime import datetime

import requests

from globals import unix_time, db_connection
from scripts import db_access


def parse_date(date_string):
    """
    Get a date from a date string as formatted by imdb
    :param date_string: YYYY-MM-DD
    :return: datetime object representing this date
    """
    return unix_time(datetime.strptime(date_string, "%Y-%m-%d"))


def send_request(api, id_val, payload):
    """
    Send a request to the api with a specific id and payload.
    :param api: api url
    :param id_val: movie or actor id
    :param payload: arguments
    :return: json data
    """
    response = requests.get(api + str(id_val), params=payload, timeout=0.1)
    response.raise_for_status()
    return response.json()


def get_birthday(id_val):
    """
    Get the birthday from a person's id.
    :param id_val: person id
    :return: unix birthdate
    """
    return parse_date(send_request(person_api, id_val, {'api_key': api_key})['birthday'])


def get_director(crew):
    """
    Get the id and name of the director from a crew list.
    :param crew: json data of crew from request
    :return: name, dir_id of director or None if not found
    """
    dir_id = None
    director_name = None
    for entry in crew:
        if entry['job'] == 'Director':
            dir_id = entry['id']
            director_name = entry['name']
    if dir_id is None:
        return None, None
    return director_name, dir_id


with open('tmdb.key', 'r') as key_file:
    api_key = key_file.read().replace('\n', '')

movie_api = 'http://api.themoviedb.org/3/movie/'
image_api = 'http://image.tmdb.org/t/p/w185/'
person_api = 'http://api.themoviedb.org/3/person/'


movie_id = 550
for movie_id in range(550, 551):
    # get a cursor
    curs = db_connection.cursor()
    # get the data from api
    data = send_request(movie_api, movie_id, {'api_key': api_key, 'append_to_response': 'credits'})
    # get variables
    title = data['title']
    # check if movie already entered
    mid = db_access.lookup_movie(title)
    if mid is not None:
        # already did this movie
        continue
    # otherwise, enter the movie

    # start with director (see if already in the database)
    dir_name, dir_id = get_director(data['credits']['crew'])
    uid = db_access.lookup_user(dir_name)
    if uid is None:
        # no user found, must add the user
        uid = db_access.make_user(dir_name)
        # and add that user to the director table with DoB
        dir_dob = get_birthday(dir_id)
        db_access.make_director(uid, dir_name, dir_dob)
    else:
        # already a user now we have to check if the user is in either the actor or director table
        if db_access.get_director_dob(uid) is None:
            # not in directors, check actors
            dir_dob = db_access.get_actor_dob(uid)
            if dir_dob is None:
                # not in directors or actors, add to directors
                dir_dob = get_birthday(dir_id)
                db_access.make_director(uid, dir_name, dir_dob)
            else:
                # director is already in actor, so we can take date of birth from there
                db_access.make_director(uid, dir_name, dir_dob)

    # now we are guaranteed to have a director, start entering movie
    released = parse_date(data['release_date'])
    db_access.make_movie(uid, title, released)

    """
    # movie done, now enter actors
    cast = data['credits']['cast']
    for actor in cast:
        # check for user in user table based on name
        uid = db_access.lookup_user(actor['name'])
        if uid is None:
            # not found, must make user
            uid = db_access.make_user(actor['name'])

    poster_url = image_api + data['poster_path']

    cast = data['credits']['cast']
    """
