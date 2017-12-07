import sqlite3
import os

import re

from datetime import datetime
from validate_email import validate_email
from flask import Blueprint, render_template, abort, request

entry_api = Blueprint('entry_api', __name__)

db_connection = sqlite3.connect(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ym.db'
    )
)


def check_user():
    return True


@entry_api.route("/entry")
def entry_index():
    if not check_user():
        abort(403)
    return render_template('entry/index.html')


@entry_api.route("/entry/user", methods=['POST', 'GET'])
def user_entry():
    if not check_user():
        abort(403)
    message = None
    if request.method == 'GET':
        return render_template('entry/user.html', message=message)
    elif request.method == 'POST':
        try:
            u_name = request.form['u_name']
            email = request.form['email']
        except KeyError:
            message = 'bad form data'
            return render_template('entry/user.html', message=message), 400
        if (not re.match(r'[a-z0-9]+', u_name)) or len(u_name) > 40:
            message = "u_name must be alphanumeric and at most 40 characters"
            return render_template('entry/user.html', message=message), 400
        if not validate_email(email):
            message = "invalid email format"
            return render_template('entry/user.html', message=message), 400
        try:
            cur = db_connection.cursor()
            cur.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", (u_name, email))
            uid = cur.lastrowid
            db_connection.commit()
            inserted_row = cur.execute("SELECT * FROM USER WHERE UID=?", (uid,))
            message = 'inserted new user successfully: ' + str(inserted_row.fetchone())
            return render_template('entry/user.html', message=message), 201
        except sqlite3.Error as err:
            print(err)
            db_connection.rollback()
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/user.html', message=message), 400
    else:
        abort(405)


@entry_api.route("/entry/admin", methods=['POST', 'GET'])
def admin_entry():
    if not check_user():
        abort(403)
    message = None
    curs = db_connection.cursor()
    curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM ADMIN) ORDER BY UID")
    users = curs.fetchall()
    if request.method == 'GET':
        return render_template('entry/admin.html', users=users, message=message)
    elif request.method == 'POST':
        try:
            uid = request.form['uid']
            position = request.form['position']
        except KeyError:
            message = 'bad form data'
            return render_template('entry/admin.html', users=users, message=message), 400
        if not re.match(r'[0-9]+', uid):
            message = "uid must be numeric"
            return render_template('entry/admin.html', users=users, message=message), 400
        if (not re.match(r'[a-zA-z_]+', position)) or len(position) > 20:
            message = "position must be alpha characters and underscores and at most 20 characters"
            return render_template('entry/admin.html', users=users, message=message), 400
        try:
            cur = db_connection.cursor()
            cur.execute("INSERT INTO ADMIN VALUES (?, ?)", (uid, position))
            uid = cur.lastrowid
            db_connection.commit()
            inserted_row = cur.execute("SELECT * FROM ADMIN WHERE UID=?", (uid,))
            message = 'inserted new user successfully: ' + str(inserted_row.fetchone())
            curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM ADMIN) ORDER BY UID")
            users = curs.fetchall()
            return render_template('entry/admin.html', users=users, message=message), 201
        except sqlite3.Error as err:
            print(err)
            db_connection.rollback()
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/admin.html', users=users, message=message), 400
    else:
        abort(405)


@entry_api.route("/entry/director", methods=['POST', 'GET'])
def director_entry():
    if not check_user():
        abort(403)
    message = None
    curs = db_connection.cursor()
    curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM DIRECTOR) ORDER BY UID")
    users = curs.fetchall()
    curs.execute("SELECT MID, title FROM MOVIE")
    movies = curs.fetchall()
    if request.method == 'GET':
        return render_template('entry/director.html', users=users, movies=movies, message=message)
    elif request.method == 'POST':
        try:
            uid = request.form['uid']
            famous_for = request.form['mid']
            given_name = request.form['given_name']
            dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        except KeyError:
            message = 'bad form data'
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        except ValueError:
            message = 'bad date format'
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        if not re.match(r'[0-9]+', uid):
            message = "uid must be numeric"
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        if not (re.match(r'[0-9]+', famous_for) or famous_for == "NULL"):
            message = "famous for mid must be numeric or NULL"
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        if (not re.match(r'[a-zA-z ]+', given_name)) or len(given_name) > 40:
            message = "name must be alpha characters and spaces and at most 40 characters"
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
        try:
            cur = db_connection.cursor()
            if famous_for == "NULL":
                cur.execute("INSERT INTO DIRECTOR VALUES (?, NULL, ?, ?)", (uid, given_name, dob.timestamp()))
            else:
                cur.execute("INSERT INTO DIRECTOR VALUES (?, ?, ?, ?)", (uid, famous_for, given_name, dob.timestamp()))
            uid = cur.lastrowid
            db_connection.commit()
            inserted_row = cur.execute("SELECT * FROM DIRECTOR WHERE UID=?", (uid,))
            message = 'inserted new user successfully: ' + str(inserted_row.fetchone())
            curs.execute("SELECT UID, u_name FROM USER WHERE USER.UID NOT IN (SELECT UID FROM DIRECTOR) ORDER BY UID")
            users = curs.fetchall()
            return render_template('entry/director.html', users=users, movies=movies, message=message), 201
        except sqlite3.Error as err:
            print(err)
            db_connection.rollback()
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/director.html', users=users, movies=movies, message=message), 400
    else:
        abort(405)


@entry_api.route("/entry/actor", methods=['POST', 'GET'])
def actor_entry():
    if not check_user():
        abort(403)
    return render_template('entry/actor.html')


@entry_api.route("/entry/movie", methods=['POST', 'GET'])
def movie_entry():
    if not check_user():
        abort(403)
    return render_template('entry/movie.html')


@entry_api.route("/entry/review", methods=['POST', 'GET'])
def review_entry():
    if not check_user():
        abort(403)
    return render_template('entry/review.html')


@entry_api.route("/entry/acted", methods=['POST', 'GET'])
def acted_entry():
    if not check_user():
        abort(403)
    return render_template('entry/acted.html')


@entry_api.route("/entry/poster", methods=['POST', 'GET'])
def poster_entry():
    if not check_user():
        abort(403)
    return render_template('entry/poster.html')


@entry_api.route("/entry/bulk", methods=['GET', 'POST'])
def bulk_entry():
    if not check_user():
        abort(403)
    message = None
    if request.method == 'GET':
        return render_template('entry/bulk.html', message=message)
    elif request.method == 'POST':
        try:
            u_name = request.form['u_name']
            email = request.form['email']
        except KeyError:
            message = 'bad form data'
            return render_template('entry/bulk.html', message=message)
        if (not re.match(r'[a-z0-9]+', u_name)) or len(u_name) > 40:
            message = "u_name must be alphanumeric and at most 40 characters"
            return render_template('entry/bulk.html', message=message)
        if not validate_email(email):
            message = "invalid email format"
            return render_template('entry/bulk.html', message=message)
        try:
            cur = db_connection.cursor()
            cur.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", (u_name, email))
            uid = cur.lastrowid
            db_connection.commit()
            inserted_row = cur.execute("SELECT * FROM USER WHERE UID=?", (uid,))
            message = 'inserted new user successfully: ' + str(inserted_row.fetchone())
            return render_template('entry/bulk.html', message=message)
        except sqlite3.Error as err:
            print(err)
            db_connection.rollback()
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/bulk.html', message=message)
    else:
        abort(405)
