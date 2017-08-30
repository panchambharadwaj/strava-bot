from stravalib.client import Client
client = Client()
code = 'd19b6f7c6af6ae86c2c80c1f56467ef6f89cd792' # or whatever your framework does
access_token = client.exchange_code_for_token(client_id=19885, client_secret='6d545857fc12a202030b56259b1d7d85a2cba5aa', code=code)
client.access_token = access_token
athlete = client.get_athlete()
print("For {id}, I now have an access token {token}".format(id=athlete.id, token=access_token))