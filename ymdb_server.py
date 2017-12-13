import secrets

from flask import Flask, render_template, abort

from browse import browse_api
from globals import db_connection, from_unix_time
from entry import entry_api
from search import search_api
from accounts import accounts_api

app = Flask(__name__)
app.register_blueprint(browse_api)
app.register_blueprint(entry_api)
app.register_blueprint(search_api)
app.register_blueprint(accounts_api)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<mid>')
def view_movie(mid):
    """
    View a movie's details.
    :param mid: movie id to lookup
    :return: rendered template with movie name, director, poster, reviews, etc.
    """
    # first check that mid is an int
    try:
        mid = int(mid)
    except ValueError:
        abort(400)

    # check if the movie is in the database
    curs = db_connection.cursor()
    curs.execute('SELECT MID, director_UID, title, release_date FROM MOVIE WHERE MID = ?', (mid, ))
    movie_row = curs.fetchone()
    # if not found, then don't render
    if movie_row is None:
        # TODO: render a 404
        abort(404)
        return
    # otherwise, get other info, starting with poster
    curs.execute('SELECT img FROM POSTER WHERE MID = ?', (mid,))
    poster_row = curs.fetchone()
    if poster_row is None:
        poster_name = None
    else:
        poster_name = poster_row[0]

    # now get director
    if movie_row[1] is None:
        director_name = 'n/a'
    else:
        director_name = movie_row[1]

    # now set title
    title = movie_row[2]

    # set release date
    if movie_row[3] is None:
        released = 'n/a'
    else:
        released = from_unix_time(movie_row[3])

    # get actors
    curs.execute('SELECT UID, character_role FROM ACTED_IN WHERE MID = ?', (mid,))
    character_rows = curs.fetchall()
    actors = []
    characters = []
    for row in character_rows:
        curs.execute('SELECT given_name FROM ACTOR WHERE UID = ?', (row[0],))
        actors.append(curs.fetchone()[0])
        characters.append(row[1])

    # get reviews
    curs.execute('SELECT UID, text, rating, created_date FROM REVIEW WHERE MID = ? ORDER BY created_date', (mid,))
    review_rows = curs.fetchall()
    usernames = []
    reviews = []
    ratings = []
    dates = []
    for row in review_rows:
        curs.execute('SELECT u_name FROM USER WHERE UID = ?', (row[0],))
        usernames.append(curs.fetchone()[0])
        reviews.append(row[1])
        ratings.append(row[2])
        dates.append(row[3])

    movie_info = {
        'title': title,
        'director': director_name,
        'released': released,
    }

    character_info = [
        {'actor': actors[i], 'character': characters[i]}
        for i in range(0, len(actors))
    ]

    review_info = [
        {'username': usernames[i], 'text': reviews[i], 'rating': ratings[i], 'date': dates[i]}
        for i in range(0, len(reviews))
    ]

    # render the template with this data
    return render_template('movie.html',
                           poster=poster_name,
                           movie_info=movie_info,
                           character_info=character_info,
                           review_info=review_info
                           )


@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response


if __name__ == '__main__':
    # enable foreign key on all database connections
    db_connection.execute('PRAGMA foreign_keys = ON')

    # configure secret key for signing session cookies
    app.secret_key = secrets.token_hex(16)

    # configure max length (for limiting uploads)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # run the app (flask)
    app.run()
