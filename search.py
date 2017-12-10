import sqlite3 as sql
import os
from flask import Blueprint, render_template, request


search_api = Blueprint('search_api', __name__)
db_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'ym.db'
        )

@search_api.route("/search")
def search_index():
    return "search index"

@search_api.route('/search/rating', method = 'POST')
def search_rating():
    movie = request.form['movie']
    with sql.connect(db_path) as con:
        cur = con.cursor()
        query = "SELECT MOVIE.title, AVG(REVIEW.rating) as rating  FROM MOVIE, REVIEW WHERE MOVIE.MID == REVIEW.MID AND MOVIE.title LIKE ? GROUP BY MOVIE.title", (moive)
        cur.execute(query)
        result = cur.fetchall()
    return render_template('search/search_rating.html', result=result, moiveTile=movie)


@search_api.route('/search/director', method = 'POST')
def search_director_famours_movie():
    director = request.form['directorName']
    with sql.connect(db_path) as con:
        cur = con.cursor()
        query = "SELECT MOVIE.title, DIRECTOR.given_name FROM MOVIE, DIRECTOR WHERE MID = famous_for_MID AND DIRECTOR.given_name LIKE ?", (director)
        cur.execute(query)
        rows = cur.fetchall()
    return render_template('search/search_directorMoive.html', rows=rows, directorName=director)


@search_api.route('/search/user', method  = 'POST')
def search_user():
    user_email = request.form['email']
    with sql.connect(db_path) as con:
        cur = con.cursor()
        query = "SELECT u_name, email FROM USER WHERE u_name LIKE ?", (user_email)
        cur.execute(query)
        result = cur.fetchall()
    return render_template('search/search_userName.html', userName=result, userEmail=user_email)



    

                                
