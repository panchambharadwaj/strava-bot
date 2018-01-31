#!/usr/bin/env python
import traceback
import requests
import argparse
import sys
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def check_arg(args=None):
    try:
        parser = argparse.ArgumentParser(description="Script to update all Private Activites to Public")
        parser.add_argument("-token", "--arg_token",
                            help="Authorization token",
                            required="True")
        results = parser.parse_args(args)
        return results.arg_token
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

def get_athlete_activities(gac_data):
    try:
        gac_response = requests_retry_session(session=requests_session).get(api_athlete_activities, data=gac_data)
    except Exception:
        print("Exception while fetching athlete's activities: " + traceback.format_exc())
        sys.exit(0)
    else:
        if gac_response.status_code == 200:
            return gac_response.json()
        else:
            print("Error fetching athlete's activities. Status Code: " + str(gac_response.status_code))
            sys.exit(0)

def update_activity(ua_activity_id):
    try:
        ua_response = requests_retry_session(session=requests_session).put(api_update_activity % ua_activity_id, data=data_private)
    except Exception:
        print("Exception while updating the activity: " + traceback.format_exc())
        return False
    else:
        if ua_response.status_code == 200:
            return True
        else:
            print("Error updating the activity. Status Code: " + str(ua_response.status_code))
            return False

if __name__ == '__main__':

    token = check_arg(sys.argv[1:])

    api_athlete_activities = "https://www.strava.com/api/v3/athlete/activities"
    api_update_activity = "https://www.strava.com/api/v3/activities/%s"

    requests_session = requests.Session()
    requests_session.headers.update({'Authorization': 'Bearer ' + token})
    data_private = [('private', False)]

    page_count = 1
    while page_count > 0:
        data = [('page', page_count)]
        print("Current page: " + str(page_count))
        athlete_activities = get_athlete_activities(data)
        if len(athlete_activities) > 0:
            for parameter in athlete_activities:
                if parameter['private'] == True:
                    if update_activity(str(parameter['id'])):
                        print("Successfully updated activity " + str(parameter['id']) + " as Public")
                    else:
                        print("Failed to update activity " + str(parameter['id']) + " as Public")
        else:
            print("Completed scanning")
        page_count += 1