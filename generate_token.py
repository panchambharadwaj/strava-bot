import argparse
import traceback
import requests
import sys
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def check_arg(args=None):
    try:
        parser = argparse.ArgumentParser(description="Script to get Athlete's token")
        parser.add_argument("-clientID", "--arg_client_id",
                            help="Client ID",
                            required="True")
        parser.add_argument("-clientSecret", "--arg_client_secret",
                            help="Client Secret",
                            required="True")
        parser.add_argument("-code", "--arg_code",
                            help="Code",
                            required="True")

        results = parser.parse_args(args)

        return (results.arg_client_id, results.arg_client_secret, results.arg_code)

    except Exception:
        sys.exit(0)

def requests_retry_session(retries=5, backoff_factor=120, status_forcelist=(500, 502, 504, 403), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

def get_athletes_token():
    try:
        gat_response = requests_retry_session().post(api_get_token, data=data)
    except Exception:
        print("Exception while fetching athlete's token: " + traceback.format_exc())
    else:
        if gat_response.status_code == 200:
            return gat_response.json()['access_token']
        else:
            print("Error fetching athlete's token. Status Code: " + str(gat_response.status_code))

if __name__ == '__main__':
    client_id, client_secret, code = check_arg(sys.argv[1:])

    api_get_token = "https://www.strava.com/oauth/token"

    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code
    }

    print(get_athletes_token())