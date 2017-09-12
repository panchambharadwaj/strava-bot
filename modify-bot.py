#!/usr/bin/env python
import requests
import time
import logging
import traceback
import sys
import smtplib
import ConfigParser
import os
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def get_config_file(config_path):
    if not os.path.exists(config_path):
        print ("INI file not found in " + config_path)
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    return config

def get_config(config_path, section, setting):
    config = get_config_file(config_path)
    value = config.get(section, setting)
    return value

def log():
    logger = logging.getLogger()
    logFormatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s")
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    fileHandler = logging.FileHandler(log_path + str(time.time()) + ".log")
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    consoleHandler.setLevel(logging.INFO)
    fileHandler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

def notifyByMail(message):
    fromaddr = fromAddress
    toaddr = toAddress
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    body = message
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP(smtp, port)
    server.ehlo()
    server.starttls()
    server.login(fromAddress, password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

config_path = "/etc/strava-bot.ini"
log_path = get_config(config_path, 'Configuration', 'Log')
authorization = get_config(config_path, 'Configuration', 'Authorization')
activity_name = get_config(config_path, 'Configuration', 'Activity-Name')
bike = get_config(config_path, 'Configuration', 'Bike')
workout_type = get_config(config_path, 'Configuration', 'Workout-Type')
sleep_time = get_config(config_path, 'Configuration', 'Sleep-Time')
isMailActive = get_config(config_path, 'Email', 'isMailActive')
fromAddress = get_config(config_path, 'Email', 'fromAddress')
password = get_config(config_path, 'Email', 'password')
toAddress = get_config(config_path, 'Email', 'toAddress')
subject = get_config(config_path, 'Email', 'subject')
smtp = get_config(config_path, 'Email', 'smtp')
port = get_config(config_path, 'Email', 'port')

log()

try:
    logging.info("Strava Bot Started")

    headers = {
            'Authorization': authorization,
    }

    logging.info("Preparing Athlete's preferred bike...")
    logging.info("Selected bike: " + bike)
    athlete_resp = 'bad-code'
    while athlete_resp == 'bad-code':
        try:
            logging.info("Requesting GET https://www.strava.com/api/v3/athlete with Headers")
            athlete_resp = requests.get('https://www.strava.com/api/v3/athlete', headers=headers)
        except requests.exceptions.ConnectionError:
            logging.info("Connection refused by the server..")
            logging.info("Sleeping for 10 minutes")
            sleep(600)
            continue
    logging.info("Response Code: " + str(athlete_resp.status_code))
    if athlete_resp.status_code == 200:
        gears = athlete_resp.json()
        for search_gear in gears['bikes']:
            if search_gear['name'] == bike:
                gear_id = search_gear['id']
                logging.info("Bike ID for "+ bike + ": " + gear_id)
    else:
        logging.error("Error Requesting GET https://www.strava.com/api/v3/athlete. Status Code - " + str(athlete_resp.status_code))

    data_gear_id = [
        ('gear_id', gear_id),
        ('name', activity_name),
        ('workout_type', workout_type)
    ]

    data_per_page = [
        ('per_page', '3')
    ]

    logging.info("---------------------------------------------------------------------------------------------------")
    logging.info("---------------------------------------------------------------------------------------------------")

    while True:
        activities_resp = 'bad-code'
        while activities_resp == 'bad-code':
            try:
                logging.info("Requesting GET https://www.strava.com/api/v3/athlete/activities with Headers & Data Per Page")
                activities_resp = requests.get('https://www.strava.com/api/v3/athlete/activities', headers=headers, data=data_per_page)
            except requests.exceptions.ConnectionError:
                logging.info("Connection refused by the server..")
                logging.info("Sleeping for 10 minutes")
                sleep(600)
                continue
        logging.info("Response Code: " + str(activities_resp.status_code))
        if activities_resp.status_code == 200:
            found_count = 0
            activities = activities_resp.json()
            for activity in activities:
                if activity['trainer'] == True:
                    logging.info(
                        "Found Trainer Activity (" + str(activity['id']) + ") dated: " + activity['start_date_local'])
                    activity_gear = activity['gear_id']
                    logging.info("Found Bike ID: " + activity_gear)
                    logging.info("Checking the found bike ID with the selected bike")
                    if activity_gear <> gear_id:
                        logging.info("Bike " + bike + " is not selected")
                        update_gear_resp = 'bad-code'
                        while update_gear_resp == 'bad-code':
                            try:
                                logging.info("Requesting PUT https://www.strava.com/api/v3/activities/" + str(activity['id']) + " with Headers & Data Gear ID")
                                update_gear_resp = requests.put('https://www.strava.com/api/v3/activities/%s' % str(activity['id']), headers=headers, data=data_gear_id)
                            except requests.exceptions.ConnectionError:
                                logging.info("Connection refused by the server..")
                                logging.info("Sleeping for 10 minutes")
                                sleep(600)
                                continue
                        logging.info("Response Code: " + str(update_gear_resp.status_code))
                        if update_gear_resp.status_code == 200:
                            logging.info("For the activity: " + str(activity['id']) + " dated: " + activity['start_date_local'] + " the following has been updated - 1. Name: 'Indoor Cycling' 2. Bike: '" + bike + "' 3. Tag: 'Workout'")
                            if isMailActive == 'yes':
                                notifyByMail("Hi Chethan,\n\nFor the activity: " + str(activity['id']) + " dated: " + activity['start_date_local'] + " the following has been updated:\n\n1. Name: 'Indoor Cycling'\n2. Bike: '" + bike + "'\n3. Tag: 'Workout'")
                        else:
                            logging.error("Error Requesting GET https://www.strava.com/api/v3/activities/" + str(activity['id']) + ". Status Code - " + str(update_gear_resp.status_code))
                    else:
                        logging.info("Bike " + bike + " is already selected")
                else:
                    if activity['trainer'] == False:
                        found_count += 1
                        if found_count == 3:
                            logging.info("Trainer Activity not found")
        else:
            logging.error("Error Requesting GET https://www.strava.com/api/v3/athlete/activities. Status Code - " + str(activities_resp.status_code))

        logging.info("Sleeping for " + sleep_time + " seconds")
        logging.info("---------------------------------------------------------------------------------------------------")
        sleep(float(sleep_time))

except Exception:
    logging.error(traceback.format_exc())
except (KeyboardInterrupt, SystemExit):
    logging.info("'Select Gear Bot' Stopped")
    logging.info("---------------------------------------------------------------------------------------------------")
    sys.exit()