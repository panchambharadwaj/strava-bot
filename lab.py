import requests

headers = {
    'Authorization': 'Bearer 7dc9015af922a5260f91538b7d51da027b83f0b0',
}

data = [
  ('per_page', '1'),
]

count = 0
r = requests.get('https://www.strava.com/api/v3/athlete/activities', headers=headers, data=data)
# r = requests.get('https://www.strava.com/api/v3/athlete', headers=headers)
print r.status_code
resp = r.json()
print resp

# import requests
#
# headers = {
#     'Authorization': 'Bearer 7dc9015af922a5260f91538b7d51da027b83f0b0',
# }
#
# data = [
#   ('per_page', '1'),
# ]
#
# following_url = 'https://www.strava.com/api/v3/activities/following'
# kudos_url = 'https://www.strava.com/api/v3/activities/%s/kudos'
#
# r = requests.get(following_url, headers=headers, data=data)
# resp = r.json()
# for a in resp:
#     print a['id']
#     k = requests.post(kudos_url % a['id'], headers=headers)
#     print k.status_code
#     print k.headers
#     print k.text
# --------------------------------------------------------------------------
# from stravalib.client import Client
# client = Client()
# code = '2cc63b04b81779d16700ff037dafcf1aa5b42f86' # or whatever your framework does
# access_token = client.exchange_code_for_token(client_id=19504, client_secret='dcf5ea96f26d1916fef8cf51f8c40937487c9ab0', code=code)
# client.access_token = access_token
# athlete = client.get_athlete()
# print("For {id}, I now have an access token {token}".format(id=athlete.id, token=access_token))
# --------------------------------------------------------------------------
# import requests
#
# headers = {
#     'Authorization': 'Bearer 7dc9015af922a5260f91538b7d51da027b83f0b0',
# }
#
# data = [
#   ('name', 'Most Epic Ride EVER!!!'),
#   ('elapsed_time', '18373'),
#   ('distance', '1557840'),
#   ('start_date_local', '2017-08-08T10:02:13Z'),
#   ('type', 'Ride'),
# ]
#
# r = requests.post('https://www.strava.com/api/v3/activities', headers=headers, data=data)
# print r
# --------------------------------------------------------------------------
# import requests
#
# headers = {
#     'Authorization': 'Bearer 7dc9015af922a5260f91538b7d51da027b83f0b0',
# }
#
# r = requests.post('https://www.strava.com/api/v3/activities/1124383446/kudos', headers=headers)
# print r.status_code
# print r.text
# print r.headers
# --------------------------------------------------------------------------














