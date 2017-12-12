import random

import bs4
import requests

from globals import db_connection
from scripts.scrape_data import parse_movie, MOVIE_URL

mid_vals = random.sample(range(1, 3135393), 101010)

# get page
res = requests.get('http://www.imdb.com/chart/top')
res.raise_for_status()
page = bs4.BeautifulSoup(res.text, 'html.parser')

"""
title_elements = page.find_all('td', {'class': 'titleColumn'})
for tie in title_elements:
    imdb_id = tie.find('a')['href'].split('/')[2]
    try:
        parse_movie(imdb_id)
        print("added imdb id " + imdb_id)
    except:
        db_connection.rollback()
        print("failed to add imdb id " + imdb_id)
"""

for i in mid_vals:
    imdb_id = 'tt' + format(i, '07')
    try:
        parse_movie(imdb_id)
        print("added imdb id " + imdb_id)
    except:
        db_connection.rollback()
        print("failed to add imdb id " + imdb_id)

