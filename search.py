import sqlite3 as sql
import os
import sys
from flask import Blueprint, render_template, request


search_api = Blueprint('search_api', __name__)
db_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'ym.db'
        )


@search_api.route('/search', methods=['GET'])
def search_index():
    return render_template('search/search_index.html')


@search_api.route('/search_rating', methods=['GET', 'POST'])
def search_rating():
    if request.method == 'POST':
        movie = '%' + request.form['movie'] + '%'
        with sql.connect(db_path) as con:
            cur = con.cursor()
            query = "SELECT MOVIE.MID, MOVIE.title, AVG(REVIEW.rating) as rating  FROM MOVIE, REVIEW WHERE MOVIE.MID == REVIEW.MID AND MOVIE.title LIKE ? GROUP BY MOVIE.MID"
            cur.execute(query, (movie,))
            result = cur.fetchall()
        return render_template('search/search_rating.html', row=result)
    elif request.method == 'GET':
        return render_template('search/search_rating.html', row='')


@search_api.route('/search_directory_famous_movies', methods=['POST', 'GET'])
def search_directory_famous_movies():
    if request.method == 'POST':
        director = '%' + request.form['directorName'] + '%'
        with sql.connect(db_path) as con:
            cur = con.cursor()
            query = "SELECT MOVIE.MID, MOVIE.title, DIRECTOR.given_name FROM MOVIE, DIRECTOR WHERE MID = famous_for_MID AND DIRECTOR.given_name LIKE ?"
            cur.execute(query, (director,))
            rows = cur.fetchall()
        return render_template('search/search_directorMovie.html', row=rows)
    elif request.method == 'GET':
        return render_template('search/search_directorMovie.html', row='')


@search_api.route('/search_user', methods=['POST', 'GET'])
def search_user():
    if request.method == 'GET':
        return render_template('search/search_user.html', result='')
    elif request.method == 'POST':
        user = '%' + request.form['u_name'] + '%'
        with sql.connect(db_path) as con:
            cur = con.cursor()
            query = "SELECT UID, u_name, email FROM USER WHERE u_name LIKE ?"
            cur.execute(query, (user,))
            result = cur.fetchall()
        return render_template('search/search_user.html', result=result)
