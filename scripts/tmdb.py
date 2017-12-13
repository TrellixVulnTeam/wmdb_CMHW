from datetime import datetime

import requests
from urllib3.exceptions import ReadTimeoutError

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
    # do a loop on the request limiting error code
    s_code = 429
    while s_code == 429:
        # loop until we aren't getting the error code
        response = requests.get(api + str(id_val), params=payload, timeout=0.25)
        s_code = response.status_code
    return response.json()


def get_birthday(id_val):
    """
    Get the birthday from a person's id.
    :param id_val: person id
    :return: unix birthdate
    """
    # get the data from server
    try:
        # try to get the data from server, but timeout after some duration
        person_data = send_request(person_api, id_val, {'api_key': api_key})
    except ReadTimeoutError:
        # not that big of a deal to be missing a birthdate
        return None
    # if birthday isn't available, return None
    if 'birthday' not in person_data:
        return None
    dob_str = person_data['birthday']
    # if no value, return none
    if dob_str is None:
        return None
    # otherwise, return unix time
    try:
        # if we can't format the string, give up
        return parse_date(dob_str)
    except ValueError:
        # return none if not able to parse
        return None


def get_director(crew):
    """
    Get the id and name of the director from a crew list.
    :param crew: json data of crew from request
    :return: name, dir_id of director or None if not found
    """
    director_id = None
    director_name = None
    for entry in crew:
        if entry['job'] == 'Director':
            director_id = entry['id']
            director_name = entry['name']
    if director_id is None:
        return None, None
    return director_name, director_id


def enter_actor(role_json):
    """
    Enter an actor into the database after checking if user exists in other tables
    :param role_json: role information
    :return: uid of new (or existing) actor
    """
    # first see if actor has a uid
    actor_fullname = role_json['name']
    actor_id = role_json['id']
    act_uid = db_access.lookup_user(actor_fullname)
    if act_uid is None:
        # no user found, must add the user
        act_uid = db_access.make_user(actor_fullname)
        # and add that user to the director table with DoB
        act_dob = get_birthday(actor_id)
        db_access.make_actor(act_uid, actor_fullname, act_dob)
    else:
        # already a user now we have to check if the user is in either the actor or director table
        if db_access.get_actor_dob(act_uid) is None:
            # not in actors, check directors
            act_dob = db_access.get_director_dob(act_uid)
            if act_dob is None:
                # not in directors or actors, add to actors after getting birthdate
                act_dob = get_birthday(actor_id)
                db_access.make_actor(act_uid, actor_fullname, act_dob)
            else:
                # actor is already in director, so we can take date of birth from there
                db_access.make_actor(act_uid, actor_fullname, act_dob)
    # return the uid of actor (created or existing)
    return act_uid


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
    mid = db_access.make_movie(uid, title, released)

    # movie is in, start adding actors
    cast = data['credits']['cast']
    for role_index in range(0, min(len(cast), 5)):
        # create or find the actor
        actor_uid = enter_actor(cast[role_index])
        # insert the role into acted_in
        character = cast[role_index]['character']
        db_access.make_role(mid, actor_uid, character)

    """
    poster_url = image_api + data['poster_path']
    """
