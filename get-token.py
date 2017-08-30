from stravalib.client import Client
client = Client()
code = '' # or whatever your framework does
access_token = client.exchange_code_for_token(client_id=1234, client_secret='', code=code)
client.access_token = access_token
athlete = client.get_athlete()
print("For {id}, I now have an access token {token}".format(id=athlete.id, token=access_token))