import re
import sqlite3
from datetime import datetime

import bcrypt
from flask import Blueprint, request, abort, render_template, session, redirect, url_for, current_app
from validate_email import validate_email

from globals import db_connection

accounts_api = Blueprint('accounts_api', __name__)

"""
Account privileges are as follows, each level possessing the privilege of the previous levels.
public:
    browse movie table
    search movies through front page
    see reviews through front page
user:
    create reviews/ratings through front page (record submitted-by uid)
moderator:
    browse user table
    browse admin table
    browse director
    browse actor
    browse review
    browse acted_in
    browse poster
    data entry for director
    data entry for actor
    data entry for movie
    data entry for review
    data entry for acted_in
    data entry for poster
admin:
    data entry for user
    data entry for admin
    bulk data entry
"""


def check_moderator():
    """
    Check session for moderator status or above.
    :return: true iff the request came from a user with moderator or admin status
    """
    if 'uid' in session:
        curs = db_connection.cursor()
        curs.execute('SELECT UID, position FROM ADMIN WHERE UID==?', (session['uid'],))
        rows = curs.fetchall()
        if len(rows) == 1:
            uid, position = rows[0]
            if uid == session['uid'] and (position == 'admin' or position == 'moderator'):
                return True
    return False


def check_admin():
    """
    Check session for admin status.
    :return: true iff the request came from a user with moderator or admin status
    """
    if 'uid' in session:
        curs = db_connection.cursor()
        curs.execute('SELECT UID, position FROM ADMIN WHERE UID==?', (session['uid'],))
        rows = curs.fetchall()
        if len(rows) == 1:
            uid, position = rows[0]
            if uid == session['uid'] and position == 'admin':
                return True
    return False


@accounts_api.route("/forbidden")
def forbidden():
    account_type = request.args.get('account_type')
    resource = request.args.get('resource')
    return render_template('accounts/denied.html', account_type=account_type, resource=resource), 403


@accounts_api.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # post requests perform login
        if 'username' in request.form:
            # get the username field
            username = request.form['username']
        else:
            # abort if field not present
            abort(400)
            return
        if 'password' in request.form:
            # get the password field
            password = request.form['password']
        else:
            # abort if field not present
            abort(400)
            return
        # have username and password, check for validity
        curs = db_connection.cursor()
        # lookup user and hashed password based on username
        curs.execute(
            'SELECT USER.UID, u_name, pass_hash FROM USER, PASSWORD WHERE u_name==? AND USER.UID==PASSWORD.UID',
            (username,)
        )
        uid_rows = curs.fetchall()
        if len(uid_rows) != 1:
            # user not found (or if greater than zero, some bigger problems are happening)
            message = 'Username or Password Incorrect'
            return render_template('accounts/login.html', message=message)
        # have user info, check password
        uid, u_name, pass_hash = uid_rows[0]
        # using bcrypt to store passwords (see account creation page)
        if bcrypt.checkpw(password.encode('utf-8'), pass_hash):
            # password match, set session variables
            session['uid'] = uid
            session['u_name'] = u_name
            session['login_time'] = datetime.now()
            session.logged_in = True
            return redirect(url_for('index'))
        else:
            # password didn't match
            message = 'Username or Password Incorrect'
            return render_template('accounts/login.html', message=message)
    elif request.method == 'GET':
        # get requests serve login page
        return render_template('accounts/login.html', message=None)
    else:
        # not get or post (shouldn't happen) abort
        abort(405)
        return


@accounts_api.route('/logout')
def logout():
    # remove session info if present
    session.pop('uid', None)
    session.pop('u_name', None)
    session.pop('login_time', None)
    session.logged_in = False
    # redirect to login page
    return redirect(url_for('accounts_api.login'))


@accounts_api.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        # get requests server signup page
        return render_template('accounts/signup.html', message=None)
    elif request.method == 'POST':
        # post requests create account
        # try to get each parameter
        try:
            # get the username field if it's there
            username = request.form['username']
            # get the email if exists
            email = request.form['email']
            # get password from form
            password = request.form['password']
            # get repassword from form
            repassword = request.form['repassword']
        except KeyError as err:
            # bad form if any key not present
            message = 'bad form data, missing ' + str(err)
            return render_template('accounts/signup.html', message=message), 400
        if not re.match(r'[a-zA-Z0-9_]+', username) or len(username) > 20:
            # bad username
            message = 'username must only contain alphanumeric and underscore characters, less than 20 long'
            return render_template('accounts/signup.html', message=message), 400
        if not validate_email(email):
            # bad email
            message = 'invalid email format'
            return render_template('accounts/signup.html', message=message), 400
        if len(password) < 12:
            # short password
            # TODO: make better password requirements
            message = 'password must be at least 12 characters long'
            return render_template('accounts/signup.html', message=message), 400
        if password != repassword:
            # passwords don't match
            message = 'passwords do not match'
            return render_template('accounts/signup.html', message=message), 400
        # all fields validated, check for existing username or email
        curs = db_connection.cursor()
        curs.execute('SELECT UID FROM USER WHERE u_name==? OR email==?', (username, email))
        existing = curs.fetchall()
        if len(existing) != 0:
            # email or username already in database
            message = 'username or email is already taken'
            return render_template('accounts/signup.html', message=message), 400
        # username and email are good, add user
        try:
            # don't commit until user and password are set
            curs.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", (username, email))
            uid = curs.lastrowid
            curs.execute('INSERT INTO PASSWORD VALUES (?, ?)',
                         (uid, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())))
            db_connection.commit()
            session['uid'] = uid
            session['u_name'] = username
            session['login_time'] = datetime.now()
            session.logged_in = True
            return redirect(url_for('index'))
        except sqlite3.Error as err:
            # couldn't insert, rollback and log issue
            db_connection.rollback()
            current_app.logger.info('failure to insert new user: ' + str(err))
            message = 'could not create account'
            return render_template('accounts/signup.html', message=message), 400
