import sqlite3

from flask import Blueprint

browse_api = Blueprint('browse_api', __name__)


@browse_api.route("/browse")
def browse_index():
    return "browse index"


@browse_api.route("/browse/user")
def browse_user():
    con = sqlite3.connect("ym.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from USER")

    rows = cur.fetchall();
    return render_template("browse_user.html", rows=rows)

@browse_api.route("/browse/admin")
def browse_admin():
    con = sqlite3.connect("ym.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from ADMIN")

    rows = cur.fetchall();
    return render_template("browse_admin.html", rows=rows)

@browse_api.route("/browse/director")
def browse_director():
    con = sqlite3.connect("ym.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from DIRECTOR")

    rows = cur.fetchall();
    return render_template("browse_director.html", rows=rows)

@browse_api.route("/browse/actor")
def browse_actor():
    con = sqlite3.connect("ym.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from ACTOR")

    rows = cur.fetchall();
    return render_template("browse_actor.html", rows=rows)

@browse_api.route("/browse/movie")
def browse_moive():
    con = sqlite3.connect("ym.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from MOVIE")

    rows = cur.fetchall();
    return render_template("browse_movie.html", rows=rows)

@browse_api.route("/browse/review")
def browse_review():
    con = sqlite3.connect("ym.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from REVIEW")

    rows = cur.fetchall();
    return render_template("browse_review.html", rows=rows)

@browse_api.route("/browse/acted_in")
def browse_acted_in():
    con = sqlite3.connect("ym.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from ACTED_IN")

    rows = cur.fetchall();
    return render_template("browse_acted_in.html", rows=rows)