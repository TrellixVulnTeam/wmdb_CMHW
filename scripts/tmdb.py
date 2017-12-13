import random
import urllib
from datetime import datetime

import os
import requests
from PIL import Image
from urllib3.exceptions import ReadTimeoutError

from entry import mid_filename
from globals import unix_time, POSTER_DIR, db_connection
from scripts import db_access


MAX_USER_UID = 1104


def enter_movie(movie_id):
    """
    Grab, parse, and enter the data for a given movie. Reuses actors/directors based on name.
    :param movie_id: the tmdb api movie id
    :return: the internal mid for this movie in MOVIE table
    """
    # print id for tracking progress
    print(movie_id)
    # get the data from api
    data = send_request(movie_api, movie_id, {'api_key': api_key, 'append_to_response': 'credits'})
    # get variables
    title = data['title']
    # check if movie already entered
    mid = db_access.lookup_movie(title)
    if mid is not None:
        # already did this movie
        return mid
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
        if db_access.get_director_dob(uid) is False:
            # not in directors, check actors
            dir_dob = db_access.get_actor_dob(uid)
            if dir_dob is False:
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

    # characters are entered, get the poster if available
    if 'poster_path' in data and data['poster_path'] is not None:
        poster_url = image_api + data['poster_path']
        poster_image = Image.open(urllib.request.urlopen(poster_url))
        # save the poster
        poster_image.save(os.path.join(POSTER_DIR, mid_filename(mid)))
        # add path to poster database
        db_access.make_poster(mid, mid_filename(mid))

    enter_reviews(mid, tmdb_id)

    return mid


def enter_reviews(internal_mid, tmdb_mid):
    """
    Enter three reviews for the specified movie by getting info from api.
    :param internal_mid: mid from our database
    :param tmdb_mid: id from tmdb
    :return: number of reviews added
    """
    # get the data from api
    data = send_request(movie_api, tmdb_mid + '/reviews', {'api_key': api_key})
    # get the total results
    num_reviews = data['total_results']
    count = 0
    uids = random.sample(range(1, MAX_USER_UID), 3)
    for i in range(0, min(num_reviews, 3)):
        text = data['results'][i]['content']
        db_access.make_review(int(internal_mid), uids[i], text, random.randint(0, 5))
        count = count + 1
    return count


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
    while True:
        # loop until we aren't getting the error code
        try:
            response = requests.get(api + str(id_val), params=payload, timeout=0.25)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            # do nothing for timeout errors (just repeat)
            continue
        except Exception as err:
            # log the error, just in case
            print(err)
            continue


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
        if db_access.get_actor_dob(act_uid) is False:
            # not in actors, check directors
            act_dob = db_access.get_director_dob(act_uid)
            if act_dob is False:
                # not in directors or actors, add to actors after getting birthdate
                act_dob = get_birthday(actor_id)
                db_access.make_actor(act_uid, actor_fullname, act_dob)
            else:
                # actor is already in director, so we can take date of birth from there
                db_access.make_actor(act_uid, actor_fullname, act_dob)
    # return the uid of actor (created or existing)
    return act_uid


def discover_year(year, id_log):
    """
    Log into the specified file at most 200 movie ids from this year. Sorts by vote count, so we get the 1500 most
    voted-on movies if possible.
    :param year: year to search
    :param id_log: open appending file for logging ids
    :return: number of ids logged
    """
    count = 0
    for i in range(1, 1001):
        print('year: ' + str(year) + ' page:' + str(i).rjust(5))
        req_args = {'api_key': api_key,
                    'sort_by': 'vote_count.desc',
                    'include_adult': 'false',
                    'primary_release_year': year,
                    'include_video': 'false',
                    'page': str(i)}
        data_page = send_request(discover_api, '', req_args)
        for item in data_page['results']:
            id_log.write(str(item['id']) + '\n')
            count = count + 1
            if count == 200:
                return count
        if i == data_page['total_pages']:
            return count
    return count


def discover_ids(filename):
    """
    Log to tmdb_ids.txt ids from every year 1950-present. Uses discover_year to limit count per year.
    :return: None
    """
    count = 0
    with open(filename, 'a') as id_log:
        for year in range(1950, 2018):
            print(count)
            count = count + discover_year(year, id_log)
            if count > 101000:
                return


# --------------------------------------------------- begin script --------------------------------------------------- #
with open('tmdb.key', 'r') as key_file:
    api_key = key_file.read().replace('\n', '')

movie_api = 'http://api.themoviedb.org/3/movie/'
image_api = 'http://image.tmdb.org/t/p/w185/'
person_api = 'http://api.themoviedb.org/3/person/'
discover_api = 'http://api.themoviedb.org/3/discover/movie'

dummy_user_max_uid = 1104

# discover_ids('tmdb_ids.txt')
with open('temp_ids.txt', 'r') as id_file:
    for tmdb_id in id_file:
        try:
            mid = enter_movie(tmdb_id)
        except Exception as err:
            print('failed on tmdb_id ' + str(tmdb_id))
            db_connection.rollback()
            print(err)
            # just keep going
            # raise err

