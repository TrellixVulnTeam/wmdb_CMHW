import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, abort

global db_connection

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/movies/', defaults={'title': None})
@app.route('/movies/<string:title>')
def movie_search(title):
    if title is None:
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM MOVIE")
        rows = cur.fetchall()
    else:
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM MOVIE WHERE TITLE=?", title)
        rows = cur.fetchall()

    return render_template('movie_search.html', movies=rows)


if __name__ == '__main__':
    db_connection = sqlite3.connect("ym.db")
    app.run()
