import requests

with open('api.key', 'r') as key_file:
    api_key = key_file.read().replace('\n', '')

movie_api = 'http://www.omdbapi.com/'
poster_api = 'http://img.omdbapi.com/'

payload = {'t': 'movie', 'type': 'movie', 'apikey': api_key}
r = requests.get(movie_api, params=payload)

print(r.json())
