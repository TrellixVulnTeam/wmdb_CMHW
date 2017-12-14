import sqlite3 as sql
import os
import sys
from flask import Blueprint, render_template, request


search_api = Blueprint('search_api', __name__)
db_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'ym.db'
        )


@search_api.route("/search")
def search_index():
    return "search index"



@search_api.route('/search_rating', methods=['GET', 'POST'])
def search_rating():
    if request.method == 'POST':
        movie = request.form['movie']
        with sql.connect(db_path) as con:
            cur = con.cursor()
            query = "SELECT MOVIE.title, AVG(REVIEW.rating) as rating  FROM MOVIE, REVIEW WHERE MOVIE.MID == REVIEW.MID AND MOVIE.title LIKE ? GROUP BY MOVIE.title"
            cur.execute(query, (movie,))
            result = cur.fetchall()
        return render_template('search/search_rating.html', row=result, movieTile=movie)
    elif request.method == 'GET':
        return render_template('search/search_rating.html', row='', movieTile='')



@search_api.route('/search_directory_famous_movies', methods=['POST', 'GET'])
def search_directory_famous_movies():
    if request.method == 'POST':
        director = request.form['directorName']
        with sql.connect(db_path) as con:
            cur = con.cursor()
            query = "SELECT MOVIE.title, DIRECTOR.given_name FROM MOVIE, DIRECTOR WHERE MID = famous_for_MID AND DIRECTOR.given_name LIKE ?"
            cur.execute(query, (director,))
            rows = cur.fetchall()
        return render_template('search/search_directorMovie.html', row=rows, directorName=director)
    elif request.method == 'GET':
        return render_template('search/search_directorMovie.html', row='', directorName='')

    

@search_api.route('/search_user', methods=['POST', 'GET'])
def search_user():
    if request.form == 'GET':
        return render_template('search/search_user.html', userName='', userEmail='')
    elif request.form=='POST':
        user_email = request.form['email']
        with sql.connect(db_path) as con:
            cur = con.cursor()
            query = "SELECT u_name, email FROM USER WHERE u_name LIKE ?"
            cur.execute(query, (user_email))
            result = cur.fetchall()
        return render_template('search/search_user.html', userName=result, userEmail=user_email)



# @search_api.route('/search/director', methods=['POST'])
# def search_director_famours_movie():
#     director = request.form['directorName']
#     with sql.connect(db_path) as con:
#         cur = con.cursor()
#         query = "SELECT MOVIE.title, DIRECTOR.given_name FROM MOVIE, DIRECTOR WHERE MID = famous_for_MID AND DIRECTOR.given_name LIKE ?", (director,)
#         cur.execute(query)
#         rows = cur.fetchall()
#     return render_template('search/search_directorMoive.html', rows=rows, directorName=director)


# @search_api.route('/search/user', methods=['POST'])
# def search_user():
#     user_email = request.form['email']
#     with sql.connect(db_path) as con:
#         cur = con.cursor()
#         query = "SELECT u_name, email FROM USER WHERE u_name LIKE ?", (user_email)
#         cur.execute(query)
#         result = cur.fetchall()
#     return render_template('search/search_userName.html', userName=result, userEmail=user_email)
