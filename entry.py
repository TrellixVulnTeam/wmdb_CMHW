import csv
import sqlite3
import os

import re

from datetime import datetime
from io import TextIOWrapper

from validate_email import validate_email
from flask import Blueprint, render_template, abort, request

global POSTER_DIR

entry_api = Blueprint('entry_api', __name__)

db_connection = sqlite3.connect(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ym.db'
    )
)

POSTER_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'static',
    'posters'
)


def check_user():
    return True


def unix_time(dt):
    """
    Covert datetime object to seconds to/from epoch
    :param dt: datetime object to convert
    :return: seconds from epoch (unix time), may be positive or negative
    """
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds()


@entry_api.route("/entry")
def entry_index():
    """
    Display the default page for the entry interfaces.
    :return: rendered template of entry index page
    """
    if not check_user():
        abort(403)
    return render_template('entry/index.html')


@entry_api.route("/entry/user", methods=['POST', 'GET'])
def user_entry():
    """
    Handles entering a new user. Post request must have u_name and email. Adds user with database default next UID and
    sets the created_date to now.
    :return: rendered template of user entry page
    """
    # check that the user is allowed access to entry subsystem
    if not check_user():
        # abort if not allowed
        abort(403)
    # default empty message
    message = None
    if request.method == 'GET':
        # handle get request with form page (no message)
        return render_template('entry/user.html', message=message)
    elif request.method == 'POST':
        # handle post request as entry of new user
        try:
            # get the username and email from the form
            u_name = request.form['u_name']
            email = request.form['email']
        except KeyError:
            # respond with error if form entries are not available
            message = 'bad form data'
            return render_template('entry/user.html', message=message), 400
        if (not re.match(r'[a-z0-9_]+', u_name)) or len(u_name) > 40:
            # check that username is only alphanumeric/underscore characters and no more than 40 characters
            # display error if not
            message = "u_name must be alphanumeric or underscore and at most 40 characters"
            return render_template('entry/user.html', message=message), 400
        if not validate_email(email):
            # validate the email format, error if not valid
            message = "invalid email format"
            return render_template('entry/user.html', message=message), 400
        try:
            # try to insert the new user
            cur = db_connection.cursor()
            cur.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", (u_name, email))
            # get the new user's id to display inserted result
            uid = cur.lastrowid
            # commit the changes to database
            db_connection.commit()
            # get the inserted row to display back to user
            inserted_row = cur.execute("SELECT * FROM USER WHERE UID=?", (uid,))
            # return a success message with added data
            message = 'inserted new user successfully: ' + str(inserted_row.fetchone())
            return render_template('entry/user.html', message=message), 201
        except sqlite3.Error as err:
            # catch sql errors (probably unique constraint or bad format)
            # roll back changes (just in case, probably doesn't even do anything)
            db_connection.rollback()
            # display error message
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/user.html', message=message), 400
    else:
        # if not get or post, abort (should never happen, but just in case)
        abort(405)


@entry_api.route("/entry/admin", methods=['POST', 'GET'])
def admin_entry():
    """
    Handle admin entry requests. Post request must contain uid and position fields. UID must be in the user relation.
    :return: Rendered template of admin entry page.
    """
    # check user authorization, abort if not valid
    if not check_user():
        abort(403)
    # default empty message
    message = None
    # get all users who are not already admins to prompt entry form
    curs = db_connection.cursor()
    curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM ADMIN) ORDER BY UID")
    # store viable users for displaying in template
    users = curs.fetchall()
    if request.method == 'GET':
        # respond to get requests with blank message and dropdown of potential admin users
        return render_template('entry/admin.html', users=users, message=message)
    elif request.method == 'POST':
        # handle post requests as entered admin data
        try:
            # get form data
            uid = request.form['uid']
            position = request.form['position']
        except KeyError:
            # show error if form doesn't contain required fields
            message = 'bad form data'
            return render_template('entry/admin.html', users=users, message=message), 400
        if not re.match(r'[0-9]+', uid):
            # make sure that uid is just numbers
            message = "uid must be numeric"
            return render_template('entry/admin.html', users=users, message=message), 400
        if (not re.match(r'[a-zA-z_]+', position)) or len(position) > 20:
            # ensure position is only alphanumeric/underscore and less than 21 characters
            message = "position must be alpha characters and underscores and at most 20 characters"
            return render_template('entry/admin.html', users=users, message=message), 400
        try:
            # try to insert new admin
            cur = db_connection.cursor()
            cur.execute("INSERT INTO ADMIN VALUES (?, ?)", (uid, position))
            # get UID of inserted admin for displaying result
            uid = cur.lastrowid
            # commit database changes
            db_connection.commit()
            # get the inserted admin row based on UID
            inserted_row = cur.execute("SELECT * FROM ADMIN WHERE UID=?", (uid,))
            # show success message with inserted admin data
            message = 'inserted new admin successfully: ' + str(inserted_row.fetchone())
            # get updated list of potential admins for displaying on next form
            curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM ADMIN) ORDER BY UID")
            users = curs.fetchall()
            # show success message and new list of users
            return render_template('entry/admin.html', users=users, message=message), 201
        except sqlite3.Error as err:
            # catch errors (like existing uids in admin and nonexistant uids from user)
            db_connection.rollback()
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/admin.html', users=users, message=message), 400
    else:
        # if not get or post, abort (should never happen, but just in case)
        abort(405)


@entry_api.route("/entry/director", methods=['POST', 'GET'])
def director_entry():
    """
    Handle requests for director entries. Displays available users and movies for potential directors and movies that
    made him/her famous. Post request must have form fields: uid, mid, given_name, dob. dob must be in the form of
    YYYY-mm-dd.
    :return: Rendered template, including lists of user and movie ids
    """
    # check for user authorization
    if not check_user():
        # abort if unauthorized
        abort(403)
    # default empty message
    message = None
    # get users who are not already directors for prompting form
    curs = db_connection.cursor()
    curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM DIRECTOR) ORDER BY UID")
    # store potential users to add to directors
    users = curs.fetchall()
    # get a list of all movie ids/titles to show potential famous_for movies
    curs.execute("SELECT MID, title FROM MOVIE")
    # store potential movies for famous_for movies
    movies = curs.fetchall()
    if request.method == 'GET':
        # handle get requests with blank message and potential users/movies
        return render_template('entry/director.html', users=users, movies=movies, message=message)
    elif request.method == 'POST':
        # handle post requests as data entry
        try:
            # try to get required form fields
            uid = request.form['uid']
            famous_for = request.form['mid']
            given_name = request.form['given_name']
            # cast dob to a datetime object (later converted to unix time)
            dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        except KeyError:
            # show error message if any form fields are missing
            message = 'bad form data'
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        except ValueError:
            # show error message if the date formatting fails
            message = 'bad date format'
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        if not re.match(r'[0-9]+', uid):
            # check that uid is just numbers, show error if not
            message = "uid must be numeric"
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        if not (re.match(r'[0-9]+', famous_for) or famous_for == "NULL"):
            # check that famous_for is a proper MID or NULL, show error if not
            message = "famous for mid must be numeric or NULL"
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        if (not re.match(r'[a-zA-z ]+', given_name)) or len(given_name) > 40:
            # check that given name contains only letters and spaces and is no more than 40 characters
            message = "name must be alpha characters and spaces and at most 40 characters"
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        try:
            # try to insert the director values
            cur = db_connection.cursor()
            if famous_for == "NULL":
                # insert with null MID (most cases)
                cur.execute("INSERT INTO DIRECTOR VALUES (?, NULL, ?, ?)", (uid, given_name, unix_time(dob)))
            else:
                # insert with given MID (not really sure when this would be possible)
                cur.execute("INSERT INTO DIRECTOR VALUES (?, ?, ?, ?)", (uid, famous_for, given_name, unix_time(dob)))
            # get the user id of the added director
            uid = cur.lastrowid
            # commit the changes
            db_connection.commit()
            # get the inserted director
            inserted_row = cur.execute("SELECT * FROM DIRECTOR WHERE UID=?", (uid,))
            # create success message with inserted data
            message = 'inserted new director successfully: ' + str(inserted_row.fetchone())
            # get an updated list of users who could become directors
            curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM DIRECTOR) ORDER BY UID")
            users = curs.fetchall()
            # show the template with potential users, movie ids, and with success message
            return render_template('entry/director.html', users=users, movies=movies, message=message), 201
        except sqlite3.Error as err:
            # catch sql errors, usually the foreign key constraint and unique constraint
            # rollback changes (if that even does anything)
            db_connection.rollback()
            # show error message
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
    else:
        # if not get or post, abort (should never happen, but just in case)
        abort(405)


@entry_api.route("/entry/actor", methods=['POST', 'GET'])
def actor_entry():
    """
    Handle actor entry requests. Post form must contain uid, stage_name, given_name, and dob. dob must be in format of
    YYYY-mm-dd for parsing. Generates list of potential users for promotion to actor.
    :return: rendered template including list of users who are not actors
    """
    # check for authorization
    if not check_user():
        # abort if unauthorized
        abort(403)
    # default empty message
    message = None
    # get list of users who are not already actors for prompting form
    curs = db_connection.cursor()
    curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM ACTOR) ORDER BY UID")
    # store candidate users
    users = curs.fetchall()
    if request.method == 'GET':
        # handle get requests with empty message and list of users
        return render_template('entry/actor.html', users=users, message=message)
    elif request.method == 'POST':
        # handle post requests as data entry
        try:
            # try to get the required field forms
            uid = request.form['uid']
            stage_name = request.form['stage_name']
            given_name = request.form['given_name']
            # cast dob to datetime for later converting to unix time
            dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        except KeyError:
            # show error on missing field forms
            message = 'bad form data'
            return render_template('entry/actor.html', users=users, message=message), 400
        except ValueError:
            # show error for bad date formatting
            message = 'bad date format'
            return render_template('entry/actor.html', users=users, message=message), 400
        if not re.match(r'[0-9]+', uid):
            # check that user id is only numeric
            message = "uid must be numeric"
            return render_template('entry/actor.html', users=users, message=message), 400
        if (not stage_name == "") and ((not re.match(r'[a-zA-z ]+', stage_name)) or len(stage_name) > 40):
            # check that stage name is either empty or only alphabetical characters
            message = "stage name must be alpha characters and spaces and at most 40 characters"
            return render_template('entry/actor.html', users=users, message=message), 400
        if (not re.match(r'[a-zA-z ]+', given_name)) or len(given_name) > 40:
            # check validation on given name too
            message = "name must be alpha characters and spaces and at most 40 characters"
            return render_template('entry/actor.html', users=users, message=message), 400
        try:
            # try to insert actor
            cur = db_connection.cursor()
            if stage_name == "":
                # insert on case that given name is same as stage name
                cur.execute("INSERT INTO ACTOR VALUES (?, NULL, ?, ?)", (uid, given_name, unix_time(dob)))
            else:
                # insert on case of specified stage name
                cur.execute("INSERT INTO ACTOR VALUES (?, ?, ?, ?)", (uid, stage_name, given_name, unix_time(dob)))
            # get the uid of the newly added actor
            uid = cur.lastrowid
            # commit the changes
            db_connection.commit()
            # get the newly added row
            inserted_row = cur.execute("SELECT * FROM ACTOR WHERE UID=?", (uid,))
            # success message with added row
            message = 'inserted new actor successfully: ' + str(inserted_row.fetchone())
            # get new list of potential users to add
            curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM ACTOR) ORDER BY UID")
            users = curs.fetchall()
            # show success message and new list of users
            return render_template('entry/actor.html', users=users, message=message), 201
        except sqlite3.Error as err:
            # handle errors for key constraint (foreign and unique)
            db_connection.rollback()
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/actor.html', users=users, message=message), 400
    else:
        # if not get or post, abort (should never happen, but just in case)
        abort(405)


@entry_api.route("/entry/movie", methods=['POST', 'GET'])
def movie_entry():
    """
    Handle requests for movie entries. Post requests must have fields: director_uid, title, release_date, and
    entered_uid. release_date must be in the form of YYYY-mm-dd. Uses dbms default next MID for primary key, uses now
    for the entered date.
    :return: rendered template, including list of potential directors and entered_by values
    """
    # check user authorization
    if not check_user():
        # abort if unauthorized
        abort(403)
    # default empty message
    message = None
    # get potential directors for listing in form
    curs = db_connection.cursor()
    curs.execute("SELECT DIRECTOR.UID, u_name FROM USER, DIRECTOR WHERE USER.UID == DIRECTOR.UID ORDER BY DIRECTOR.UID")
    directors = curs.fetchall()
    # get potential admins for listing in form
    curs.execute("SELECT ADMIN.UID, u_name FROM USER, ADMIN WHERE USER.UID == ADMIN.UID ORDER BY ADMIN.UID")
    admins = curs.fetchall()
    if request.method == 'GET':
        # handle get requests with empty message and list of directors and admins
        return render_template('entry/movie.html', directors=directors, admins=admins, message=message)
    elif request.method == 'POST':
        # handle post requests as data entry
        try:
            # try to get required form fields
            director_uid = request.form['director_uid']
            title = request.form['title']
            # parse date into datetime object
            release_date = datetime.strptime(request.form['release_date'], '%Y-%m-%d')
            entered_uid = request.form['entered_uid']
        except KeyError:
            # show error message if any fields missing
            message = 'bad form data'
            return render_template('entry/movie.html', directors=directors, admins=admins, message=message), 400
        except ValueError:
            # show error message if unable to parse date
            message = 'bad date format'
            return render_template('entry/movie.html', directors=directors, admins=admins, message=message), 400
        if not re.match(r'[0-9]+', director_uid):
            # show error message if director uid is not strictly numeric
            message = "director uid must be numeric"
            return render_template('entry/movie.html', directors=directors, admins=admins, message=message), 400
        if len(title) < 1 or len(title) > 40:
            # show error message if title is empty or longer than 40 characters
            message = "title must be between 1 and 40 characters long (inclusive)"
            return render_template('entry/movie.html', directors=directors, admins=admins, message=message), 400
        if not re.match(r'[0-9]+', entered_uid):
            # show error message if entered_by uid is not strictly numeric
            message = "entered uid must be numeric"
            return render_template('entry/movie.html', directors=directors, admins=admins, message=message), 400
        try:
            # try to insert the new movie entry
            cur = db_connection.cursor()
            # pass null into MID to let dbms decide next value
            cur.execute("INSERT INTO MOVIE VALUES (NULL, ?, ?, ?, ?, strftime('%s', 'now'))",
                        (director_uid, title, unix_time(release_date), entered_uid))
            # get the movie ID of the recently added movie
            mid = cur.lastrowid
            # commit the changes
            db_connection.commit()
            # get the inserted row for success message
            inserted_row = cur.execute("SELECT * FROM MOVIE WHERE MID=?", (mid,))
            message = 'inserted new movie successfully: ' + str(inserted_row.fetchone())
            # display success message and already found list of admins and directors
            return render_template('entry/movie.html', directors=directors, admins=admins, message=message), 201
        except sqlite3.Error as err:
            # handle error (like director foreign key constraint or entered_by foreign key)
            db_connection.rollback()
            # show error message on bad value
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/movie.html', directors=directors, admins=admins, message=message), 400
    else:
        # if not get or post, abort (should never happen, but just in case)
        abort(405)


@entry_api.route("/entry/review", methods=['POST', 'GET'])
def review_entry():
    """
    Handle review entry requests. Post requests must have fields: MID, UID, text, and rating. Uses current time as
    created date. MID and UID must exist in movies and users respectively. Text can be empty, but must only contain
    letters, numbers, spaces, and punctuation. Rating must be between 0 and 5.
    :return: rendered template including list of movies and users
    """
    # check that user is authorized
    if not check_user():
        # abort if not authorized
        abort(403)
    # default empty message
    message = None
    # get movies for mid dropdown
    curs = db_connection.cursor()
    curs.execute("SELECT MID, title FROM MOVIE ORDER BY MID")
    movies = curs.fetchall()
    # get users for uid dropdown
    curs.execute("SELECT UID, u_name FROM USER ORDER BY UID")
    users = curs.fetchall()
    if request.method == 'GET':
        # handle get requests with empty message and movie/user dropdowns
        return render_template('entry/review.html', movies=movies, users=users, message=message)
    elif request.method == 'POST':
        # handle post requests as data entry
        try:
            mid = request.form['mid']
            uid = request.form['uid']
            text = request.form['text']
            rating = int(request.form['rating'])
        except KeyError:
            # show error message for missing fields
            message = 'bad form data'
            return render_template('entry/review.html', movies=movies, users=users, message=message), 400
        if not re.match(r'[0-9]+', mid):
            # test for mid being strictly numeric
            message = 'mid must be numeric'
            return render_template('entry/review.html', movies=movies, users=users, message=message), 400
        if not re.match(r'[0-9]+', uid):
            # test for uid being strictly numeric
            message = 'uid must be numeric'
            return render_template('entry/review.html', movies=movies, users=users, message=message), 400
        if not re.match(r'[0-9a-zA-Z_.,"\'()!@$*=\-+&:]*', text):
            # test for text matching only alphanumeric and punctuation
            message = 'text must be alphanumeric with punctuation (no carats, braces, or octothorpes)'
            return render_template('entry/review.html', movies=movies, users=users, message=message), 400
        if rating < 0 or rating > 5:
            # make sure rating is [0:5]
            message = 'rating must be from zero to five'
            return render_template('entry/review.html', movies=movies, users=users, message=message), 400
        try:
            # try to insert the new review entry
            cur = db_connection.cursor()
            # pass now as created date for this review
            cur.execute("INSERT INTO REVIEW VALUES (?, ?, ?, ?, strftime('%s', 'now'))",
                        (mid, uid, text, rating))
            # commit changes
            db_connection.commit()
            # get the newly entered row
            inserted_row = cur.execute("SELECT * FROM REVIEW WHERE MID == ? AND UID == ?", (mid, uid))
            # show success message
            message = 'inserted new review successfully: ' + str(inserted_row.fetchone())
            return render_template('entry/review.html', movies=movies, users=users, message=message), 201
        except sqlite3.Error as err:
            # handle sql errors (probably mid, uid already existing)
            db_connection.rollback()
            # show error message on bad value
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/review.html', movies=movies, users=users, message=message), 400
    else:
        # if not get or post, abort (should never happen, but just in case)
        abort(405)


@entry_api.route("/entry/acted", methods=['POST', 'GET'])
def acted_entry():
    """
    Handle requests for entry into ACTED_IN relation. Post requests must have fields mid, uid, and character_role. MID
    and UID must be present in MOVIE and USER. Must not be present already in the relation (i.e., no actors playing
    multiple roles in the same movie).
    :return: rendered template including dropdowns for mid and uid of movies and actors
    """
    # check user authorization
    if not check_user():
        # abort if not authorized
        abort(403)
    # default empty message
    message = None
    # get movies for mid dropdown
    curs = db_connection.cursor()
    curs.execute("SELECT MID, title FROM MOVIE ORDER BY MID")
    movies = curs.fetchall()
    # get users for uid dropdown
    curs.execute("SELECT ACTOR.UID, u_name FROM USER, ACTOR WHERE USER.UID == ACTOR.UID ORDER BY ACTOR.UID")
    users = curs.fetchall()
    if request.method == 'GET':
        # handle get requests with empty message and movie/user dropdowns
        return render_template('entry/acted.html', movies=movies, users=users, message=message)
    elif request.method == 'POST':
        # handle post requests as data entry
        try:
            # get required form fields
            mid = request.form['mid']
            uid = request.form['uid']
            character_role = request.form['character_role']
        except KeyError:
            # show error message for missing fields
            message = 'bad form data'
            return render_template('entry/acted.html', movies=movies, users=users, message=message), 400
        if not re.match(r'[0-9]+', mid):
            # test for mid being strictly numeric
            message = 'mid must be numeric'
            return render_template('entry/acted.html', movies=movies, users=users, message=message), 400
        if not re.match(r'[0-9]+', uid):
            # test for uid being strictly numeric
            message = 'uid must be numeric'
            return render_template('entry/acted.html', movies=movies, users=users, message=message), 400
        if (not re.match(r'[0-9a-zA-Z\'\- ]+', character_role)) or len(character_role) > 20:
            # test character role for being alphanumeric with spaces, apostrophes, hyphens, or spaces
            message = 'character_role must be alphanumeric with spaces, apostrophes, hyphens, or spaces less than 20 ' \
                      'characters'
            return render_template('entry/acted.html', movies=movies, users=users, message=message), 400
        try:
            # try to enter the new role
            cur = db_connection.cursor()
            cur.execute('INSERT INTO ACTED_IN VALUES (?, ?, ?)', (mid, uid, character_role))
            # commit changes
            db_connection.commit()
            # get the newly entered row
            inserted_row = cur.execute("SELECT * FROM ACTED_IN WHERE MID == ? AND UID == ?", (mid, uid))
            # show success message
            message = 'inserted new role successfully: ' + str(inserted_row.fetchone())
            return render_template('entry/acted.html', movies=movies, users=users, message=message), 201
        except sqlite3.Error as err:
            # handle sql errors (probably mid, uid already existing)
            db_connection.rollback()
            # show error message on bad value
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/acted.html', movies=movies, users=users, message=message), 400
    else:
        # if not get or post, abort (should never happen, but just in case)
        abort(405)

    return render_template('entry/acted.html')


@entry_api.route("/entry/poster", methods=['POST', 'GET'])
def poster_entry():
    """
    Handle file uploads for poster data entry. POST request must contain fields mid and img. mid must be present in
    movies relation and img must be an openable image file.
    :return: rendered template including list of movies ids
    """
    # check for authorization
    if not check_user():
        # abort if unauthorized
        abort(403)
    # get the list of movies for dropdown
    curs = db_connection.cursor()
    curs.execute('SELECT MID, title FROM MOVIE')
    movies = curs.fetchall()
    if request.method == 'GET':
        # handle get requests with blank message and movie dropdown
        return render_template('entry/poster.html', movies=movies, message=None, image_name=None)
    elif request.method == 'POST':
        # handle post requests as upload
        if 'img' not in request.files:
            # show error if no file in post data
            message = 'no file uploaded'
            return render_template('entry/poster.html', movies=movies, message=message, image_name=None), 400
        try:
            # try to get field and file
            mid = request.form['mid']
            img = request.files['img']
        except KeyError:
            # show error if file not uploaded, or form data bad
            message = 'bad form data'
            return render_template('entry/poster.html', movies=movies, message=message, image_name=None), 400
        # TODO: check file type (not just extension)
        if not re.match(r'[0-9]+', mid):
            # test for mid being strictly numeric
            message = 'mid must be numeric'
            return render_template('entry/poster.html', movies=movies, message=message, image_name=None), 400
        # check for file validity
        if img.filename == '':
            # show error for empty filename
            message = 'no file selected'
            return render_template('entry/poster.html', movies=movies, message=message, image_name=None), 400
        try:
            # create new filename
            filename = str(mid) + '.png'
            # try to enter new filename in database
            cur = db_connection.cursor()
            cur.execute('REPLACE INTO POSTER VALUES (?, ?)', (mid, filename))
        except sqlite3.Error as err:
            # should update if exists, so this is a real problem
            db_connection.rollback()
            # show error message on bad value
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/poster.html', movies=movies, message=message, image_name=None), 400
        if img:
            # save the file
            img.save(os.path.join(POSTER_DIR, filename))
            # get the tuple
            cur.execute('SELECT img FROM POSTER WHERE MID==?', (mid,))
            filename = str(cur.fetchone()[0])
            # show success message
            message = 'successfully added poster file for movie id: ' + str(mid)
            return render_template('entry/poster.html', movies=movies, message=message, image_name=filename), 201
        else:
            # image not allowed
            message = 'file must be png'
            return render_template('entry/poster.html', movies=movies, message=message, image_name=None), 400
    else:
        # if not get or post, abort (should never happen, but just in case)
        abort(405)


@entry_api.route("/entry/bulk", methods=['GET', 'POST'])
def bulk_entry():
    """
    Handler for bulk entry. Post requests must upload a csv file with the correct format for the specified relation.
    Does not allow bulk loading of poster data.
    :return:
    """
    # check user authorization
    if not check_user():
        # abort if unauthorized
        abort(403)
    if request.method == 'GET':
        # get requests just get the form
        return render_template('entry/bulk.html', message=None)
    elif request.method == 'POST':
        # handle posts as data entry
        if 'csv_data' not in request.files:
            # show error if no file in post data
            message = 'no file uploaded'
            return render_template('entry/poster.html', message=message), 400
        try:
            # try to get form data
            relation = request.form['relation']
            csv_data = TextIOWrapper(request.files['csv_data'], encoding='utf-8')
        except KeyError:
            # show error for bad form
            message = 'bad form data'
            return render_template('entry/bulk.html', message=message), 400
        # TODO: check file type (not just extension)
        try:
            # try to call bulk helper function for correct relation
            if relation == 'user':
                message = bulk_user(csv_data)
            elif relation == 'admin':
                message = bulk_admin(csv_data)
            elif relation == 'director':
                message = bulk_director(csv_data)
            elif relation == 'actor':
                message = bulk_actor(csv_data)
            elif relation == 'movie':
                message = bulk_movie(csv_data)
            elif relation == 'review':
                message = bulk_review(csv_data)
            elif relation == 'acted_in':
                message = bulk_acted(csv_data)
            else:
                # if not one of predefined relations, error
                message = 'invalid relation'
                return render_template('entry/bulk.html', message=message), 400
            # if we reach this point, success
            return render_template('entry/bulk.html', message=message), 201
        except sqlite3.Error as err:
            # catch sql error from bulk entry
            message = 'rollback due to sql error: ' + str(err)
            # display error message
            return render_template('entry/bulk.html', message=message), 400
        except KeyError as err:
            # catch key error for bad csv data
            message = 'bad csv data (key error): ' + str(err)
            # display error message
            return render_template('entry/bulk.html', message=message), 400
    else:
        # if not get or post, abort (should never happen, but just in case)
        abort(405)


def bulk_connection():
    """
    Get a connection to the database that doesn't have autocommit (so we can do transactions manually)
    :return: non-auto-commit connection to database
    """
    conn = sqlite3.connect(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'ym.db'
        )
    )
    # isolation level of none allows us to commit by ourselves
    conn.isolation_level = None
    return conn


def bulk_user(file):
    # create the dictionary from csv file
    dict_reader = csv.DictReader(file)
    tuples = [(entry['u_name'], entry['email']) for entry in dict_reader]
    # make sure all emails are actually emails
    for t in tuples:
        if not validate_email(t[1]):
            raise KeyError('email not email')
    # get a connection without isolation level or autocommit
    c = bulk_connection()
    # try to enter the data
    try:
        curs = c.cursor()
        # start transaction (so we can rollback if any entries fail
        curs.execute("BEGIN")
        # try to insert all the users
        curs.executemany("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", tuples)
        # get the number of rows affected
        num_rows = curs.rowcount
        # commit the changes
        curs.execute('COMMIT')
        # close the connection
        c.close()
        # return the success message
        return 'bulk user entry success, inserted ' + str(num_rows) + ' rows'
    except sqlite3.Error as err:
        # rollback changes, close the connection, then pass the error onto caller
        curs.execute('ROLLBACK')
        c.close()
        raise err


def bulk_admin(file):
    return "admin not implemented"


def bulk_director(file):
    return "director not implemented"


def bulk_actor(file):
    return "actor not implemented"


def bulk_movie(file):
    return "movie not implemented"


def bulk_review(file):
    return "review not implemented"


def bulk_acted(file):
    return "acted_in not implemented"
