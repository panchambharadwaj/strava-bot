#!/usr/bin/env python
import logging
import os
import signal
import smtplib
import sys
import traceback
import argparse
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def check_arg(args=None):
    try:
        parser = argparse.ArgumentParser(description="Script to update trainer activity on Strava")
        parser.add_argument("-athleteName", "--arg_athlete_name",
                            help="Athlete Name",
                            required="True")
        parser.add_argument("-token", "--arg_token",
                            help="Authorization token",
                            required="True")
        parser.add_argument("-updateActivityName", "--arg_update_activity_name",
                            help="Update activity name",
                            default=None)
        parser.add_argument("-updatePrivate", "--arg_update_private",
                            help="Update if Private. Accepts Boolean type",
                            type=bool,
                            default=None)
        parser.add_argument("-updateGear", "--arg_update_gear",
                            help="Update Gear",
                            default=None)
        parser.add_argument("-updateWorkoutType", "--arg_update_workout_type",
                            help="Update workout type (12 for workout)",
                            default=None)
        parser.add_argument("-updateDescription", "--arg_update_description",
                            help="Update Description",
                            default=None)
        parser.add_argument("-emailFrom", "--arg_email_from_address",
                            help="From Email ID",
                            required="True")
        parser.add_argument("-emailPwd", "--arg_email_from_password",
                            help="From Email ID's password. Pass 'None' if there is no password required",
                            default=None)
        parser.add_argument("-emailTo", "--arg_email_to_address",
                            help="To Email ID. Must be separated by commas (without spaces) in case of multiple IDs",
                            required="True")
        parser.add_argument("-emailHost", "--arg_email_host",
                            help="Email ID Host",
                            required="True")
        parser.add_argument("-emailPort", "--arg_email_port",
                            help="Email ID Port",
                            required="True")
        parser.add_argument("-sleep", "--arg_sleep",
                            help="Sleep in seconds",
                            type=int,
                            required="True")

        results = parser.parse_args(args)

        return (results.arg_athlete_name,
                results.arg_token,
                results.arg_update_activity_name,
                results.arg_update_private,
                results.arg_update_gear,
                results.arg_update_workout_type,
                results.arg_update_description,
                results.arg_email_from_address,
                results.arg_email_from_password,
                results.arg_email_to_address.split(","),
                results.arg_email_host,
                results.arg_email_port,
                results.arg_sleep)

    except Exception:
        sys.exit(0)


def log():
    logger = logging.getLogger()
    logFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    if not os.path.exists("/var/log/strava-bot"):
        os.makedirs("/var/log/strava-bot")
    log_name = (os.path.splitext(os.path.basename(__file__))[0]) + "-" + athlete_name + "-" + datetime.now().strftime(
        '%Y-%m-%d-%H-%M-%S') + ".log"
    log_path = "/var/log/strava-bot/" + log_name
    fileHandler = logging.FileHandler(log_path)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    consoleHandler.setLevel(logging.INFO)
    fileHandler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)


def requests_retry_session(retries=5, backoff_factor=120, status_forcelist=(500, 502, 503, 504, 403), session=None):
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


def get_athlete_details():
    logging.info("Requesting " + api_athlete_details)
    try:
        gad_athlete_resp = requests_retry_session(session=requests_session).get(api_athlete_details)
    except Exception:
        logging.info("Exception while fetching athlete details: " + traceback.format_exc())
        sys.exit(0)
    else:
        logging.info(gad_athlete_resp)
        if gad_athlete_resp.status_code == 200:
            return gad_athlete_resp.json()
        else:
            logging.info("Error fetching athlete details. Status Code: " + str(gad_athlete_resp.status_code))
            sys.exit(0)


def get_gear_id(ggi_athlete_details):
    for ggi_search_gear_id in ggi_athlete_details['bikes']:
        if ggi_search_gear_id['name'] == update_gear:
            logging.info("Gear ID: " + ggi_search_gear_id['id'])
            return ggi_search_gear_id['id']


def generate_parameters_for_updating_activity_and_email():
    gpfuaae_update_activity_data = []
    gpfuaae_email_body_parameters = ""
    if update_activity_name != None:
        gpfuaae_update_activity_data.append(('name', update_activity_name))
        gpfuaae_email_body_parameters += "\nActivity Name: " + update_activity_name
    if update_private != None:
        gpfuaae_update_activity_data.append(('private', update_private))
        gpfuaae_email_body_parameters += "\nPrivate: " + update_private
    if update_gear != None:
        gpfuaae_update_activity_data.append(('gear_id', get_gear_id(get_athlete_details())))
        gpfuaae_email_body_parameters += "\nBike: " + update_gear
    if update_workout_type != None:
        gpfuaae_update_activity_data.append(('workout_type', update_workout_type))
        gpfuaae_email_body_parameters += "\nRide Type: " + get_workout_type(update_workout_type)
    if update_description != None:
        gpfuaae_update_activity_data.append(('description', update_description))
        gpfuaae_email_body_parameters += "\nDescription: " + update_description
    return (gpfuaae_update_activity_data, gpfuaae_email_body_parameters)


def get_workout_type(gwt_workout_type):
    if gwt_workout_type == "12":
        return "Workout"
    else:
        return gwt_workout_type


def get_lastest_activity():
    logging.info("Requesting: " + api_athlete_activities)
    try:
        gla_response = requests_retry_session(session=requests_session).get(api_athlete_activities,
                                                                            data=data_number_of_activities)
    except Exception:
        logging.info("Exception while fetching lastest activity: " + traceback.format_exc())
        pass
    else:
        logging.info(gla_response)
        if gla_response.status_code == 200:
            return gla_response.json()[0]
        else:
            logging.info("Error fetching lastest activity. Status Code: " + str(gla_response.status_code))
            pass


def update_activity(ua_latest_activity_id):
    logging.info("Requesting: " + api_update_activity % ua_latest_activity_id)
    try:
        ua_response = requests_retry_session(session=requests_session).put(api_update_activity % ua_latest_activity_id,
                                                                           data=data_update_activity)
    except Exception:
        logging.info("Exception while updating the latest activity: " + traceback.format_exc())
        return False
    else:
        logging.info(ua_response)
        if ua_response.status_code == 200:
            return True
        else:
            logging.info("Error updating the latest activity. Status Code: " + str(ua_response.status_code))
            return False


def is_activity_new():
    ian_is_activity_new = False
    for parameter in data_update_activity:
        if str(latest_activity[parameter[0]]) != parameter[1]:
            ian_is_activity_new = True
            logging.info("New trainer activity found")
            break
    return ian_is_activity_new


def notify_by_mail(nbm_email_subject, nbm_email_body):
    nbm_from_address = email_from_address
    nbm_to_address = email_to_address
    nbm_body = nbm_email_body
    msg = MIMEMultipart()
    msg['From'] = nbm_from_address
    msg['To'] = ", ".join(nbm_to_address)
    msg['Subject'] = nbm_email_subject
    msg.attach(MIMEText(nbm_body, 'plain'))
    text = msg.as_string()
    try:
        server = smtplib.SMTP(email_host, email_port)
        server.ehlo()
        server.starttls()
        server.login(email_from_address, email_from_password)
        server.sendmail(nbm_from_address, email_to_address, text)
    except Exception:
        logging.info("Exception in notify by mail. Exception: %s\n\n" % (traceback.format_exc()))
    finally:
        server.quit()


def signal_term_handler(signal, frame):
    logging.info('Bot was killed')
    sys.exit(0)


def main():
    while True:
        try:
            logging.info("Looking for the latest trainer activity")
            latest_activity = get_lastest_activity()
            if (latest_activity['trainer']) and (is_activity_new()):
                if update_activity(latest_activity['id']):
                    update_activity_status = "Successful"
                else:
                    update_activity_status = "Failed"
                notify_by_mail(email_subject_update % (update_activity_status, latest_activity['start_date_local']),
                               email_body_update % (
                                   athlete_name, update_activity_status, email_body_parameters, latest_activity['id']))
            else:
                logging.info("Not the latest trainer activity")
            latest_activity.clear()
            logging.info("Sleeping for " + str(bot_sleep_time) + " seconds")
            sleep(bot_sleep_time)
        except(KeyboardInterrupt, SystemExit):
            bot_stopped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.info("Bot stopped at: " + bot_stopped_at)
            notify_by_mail(email_subject_stopped % bot_stopped_at, email_body_stopped % (athlete_name))
            sys.exit(0)
        except Exception:
            logging.info("Exception: " + str(traceback.format_exc()))
            logging.info("Sleeping for 600 seconds")
            sleep(600)
            continue

            
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_term_handler)
    athlete_name, token, update_activity_name, update_private, update_gear, update_workout_type, update_description, email_from_address, email_from_password, email_to_address, email_host, email_port, bot_sleep_time = check_arg(
        sys.argv[1:])

    bot_started_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log()
    logging.info("Bot started at: " + bot_started_at)
    logging.info("Setting up the Bot")

    email_subject_started = "[Strava Bot] Started at %s"
    email_subject_update = "[Strava Bot] %s in updating the trainer activity started at %s"
    email_subject_stopped = "[Strava Bot] Stopped at %s"
    email_body_started = "Hi %s,\n\nStarted your update trainer activity bot with the below parameters:\n%s\n\nRegards,\nStrava Bot"
    email_body_update = "Hi %s,\n\n%s in updating the trainer activity with the below parameters:\n%s\n\nhttps://www.strava.com/activities/%s\n\nRegards,\nStrava Bot"
    email_body_stopped = "Hi %s,\n\nStopped your update trainer activity bot.\n\nRegards,\nStrava Bot"
    api_athlete_details = "https://www.strava.com/api/v3/athlete"
    api_athlete_activities = "https://www.strava.com/api/v3/athlete/activities"
    api_update_activity = "https://www.strava.com/api/v3/activities/%s"
    data_number_of_activities = [('per_page', '1')]

    requests_session = requests.Session()
    requests_session.headers.update({'Authorization': 'Bearer ' + token})

    data_update_activity, email_body_parameters = generate_parameters_for_updating_activity_and_email()
    logging.info("Data to update activity: " + str(data_update_activity))

    notify_by_mail(email_subject_started % bot_started_at, email_body_started % (athlete_name, email_body_parameters))

    logging.info("Bot setup completed")

    main()