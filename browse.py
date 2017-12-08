
from flask_paginate import Pagination, get_page_args
import sqlite3

import os
from flask import Blueprint, render_template, request

browse_api = Blueprint('browse_api', __name__)

db_connection = sqlite3.connect(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ym.db'
    )
)


@browse_api.route("/browse")
def browse_index():
    return render_template('browse/index.html')


@browse_api.route("/browse/user")
def browse_user():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("select * from USER")

    rows = cur.fetchall()

    rows_limited = rows[offset:(per_page+offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')


    return render_template('browse/browse_user.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/admin")
def browse_admin():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("select * from ADMIN")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_admin.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/director")
def browse_director():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("select * from DIRECTOR")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_director.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/actor")
def browse_actor():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("select * from ACTOR")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_actor.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/movie")
def browse_movie():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("select * from MOVIE")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_movie.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/review")
def browse_review():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("select * from REVIEW")

    rows = cur.fetchall();
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_review.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/acted_in")
def browse_acted_in():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("select * from ACTED_IN")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_acted_in.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )

