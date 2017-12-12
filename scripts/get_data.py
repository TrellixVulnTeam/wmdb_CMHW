import random

from scripts.scrape_data import parse_movie

mid_vals = random.sample(range(1, 3135393), 101010)

for i in mid_vals:
    imdb_id = 'tt' + format(i, '07')
    parse_movie(imdb_id)



