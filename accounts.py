from datetime import datetime

import bcrypt
from flask import Blueprint, request, abort, render_template, session, redirect, url_for

from db_connection import db_connection

accounts_api = Blueprint('accounts_api', __name__)


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
        if bcrypt.checkpw(password, pass_hash):
            # password match, set session variables
            session['uid'] = uid
            session['u_name'] = u_name
            session['login_time'] = datetime.now()
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
    # redirect to login page
    return redirect(url_for('accounts_api.login'))


@accounts_api.route('/signup')
def signup():
    return redirect(url_for('index'))
