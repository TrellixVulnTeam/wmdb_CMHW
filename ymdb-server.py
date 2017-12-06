import sqlite3
import os

from flask import Flask, flash, redirect, render_template, request, session, abort

from browse import browse_api
from entry import entry_api
from search import search_api

global db_connection

app = Flask(__name__)
app.register_blueprint(browse_api)
app.register_blueprint(entry_api)
app.register_blueprint(search_api)


@app.route('/')
def index():
    curs = db_connection.cursor()
    curs.execute('SELECT * FROM MOVIE')
    rows = curs.fetchall()
    return render_template('index.html', rows=rows)


if __name__ == '__main__':
    db_connection = sqlite3.connect(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'ym.db'
        )
    )
    app.run()
