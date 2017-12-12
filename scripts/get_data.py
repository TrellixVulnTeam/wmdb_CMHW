import random

import requests

with open('api.key', 'r') as key_file:
    api_key = key_file.read().replace('\n', '')

movie_api = 'http://www.omdbapi.com/'
poster_api = 'http://img.omdbapi.com/'

payload = {'i': 'tt0000001', 'type': 'movie', 'apikey': api_key}
r = requests.get(movie_api, params=payload)


mid_vals = random.sample(range(1, 3135393), 101010)

for i in mid_vals:
    imdb_id = 'tt' + format(i, '07')
    payload = {'i': imdb_id, 'type': 'movie', 'apikey': api_key}
    # data = requests.get(movie_api, params=payload).json()
    print(payload)



