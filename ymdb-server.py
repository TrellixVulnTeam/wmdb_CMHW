from flask import Flask, render_template

from browse import browse_api
from db_connection import db_connection
from entry import entry_api
from search import search_api

app = Flask(__name__)
app.register_blueprint(browse_api)
app.register_blueprint(entry_api)
app.register_blueprint(search_api)


@app.route('/')
def index():
    return render_template('index.html')


@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response


if __name__ == '__main__':
    # enable foreign key on all database connections
    db_connection.execute('PRAGMA foreign_keys = ON')

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.run()