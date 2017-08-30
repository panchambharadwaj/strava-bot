import requests
import time
from time import sleep
import logging
import traceback
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def notifyByMail(message):
    fromaddr = 'pancham.geek@gmail.com'
    toaddr = ['chethanram@gmail.com', 'phaneesh.n@gmail.com', 'panchamrb@gmail.com']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Subject'] = 'Strava Alert | Select Gear Bot'
    body = message
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('pancham.geek@gmail.com', 'Kg8b2k78^pvx')
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

try:
    logger = logging.getLogger()
    logFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    fileHandler = logging.FileHandler("/var/log/select-gear-bot-" + str(time.time()) + ".log")
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    consoleHandler.setLevel(logging.INFO)
    fileHandler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    logging.info("'Select Gear Bot' Started")

    bike = "Indoor Trainer"

    headers = {
            'Authorization': 'Bearer b344824d8c65723a4bd1d0c9ab36f709b7dab09a',
    }

    data_per_page = [
      ('per_page', '3'),
    ]

    logging.info("Preparing Athlete's preferred bike...")
    logging.info("Selected bike: " + bike)
    logging.info("Requesting GET https://www.strava.com/api/v3/athlete with Headers")

    athlete_resp = requests.get('https://www.strava.com/api/v3/athlete', headers=headers)
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
    ]

    logging.info("---------------------------------------------------------------------------------------------------")
    logging.info("---------------------------------------------------------------------------------------------------")

    while True:

        logging.info("Requesting GET https://www.strava.com/api/v3/athlete/activities with Headers & Data Per Page")
        activities_resp = requests.get('https://www.strava.com/api/v3/athlete/activities', headers=headers, data=data_per_page)
        logging.info("Response Code: " + str(activities_resp.status_code))
        if activities_resp.status_code == 200:
            found_count = 0
            activities = activities_resp.json()
            for activity in activities:
                if activity['trainer'] == True:
                    logging.info("Found Trainer Activity (" + str(activity['id']) + ") dated: " + activity['start_date_local'])
                    activity_gear = activity['gear_id']
                    logging.info("Found Bike ID: " + activity_gear)
                    logging.info("Checking the found bike ID with the bike to select")
                    if activity_gear <> gear_id:
                        logging.info("Bike " + bike + " is not selected")
                        logging.info("Requesting PUT https://www.strava.com/api/v3/activities/" + str(activity['id']) + " with Headers & Data Gear ID")
                        update_gear_resp = requests.put('https://www.strava.com/api/v3/activities/%s' % str(activity['id']), headers=headers, data=data_gear_id)
                        logging.info("Response Code: " + str(update_gear_resp.status_code))
                        if update_gear_resp.status_code == 200:
                            logging.info("Updated bike to " + bike)
                            notifyByMail("Hi Chethan,\n\nUpdated bike to " + bike + " for Trainer Activity (" + str(activity['id']) + ") dated: " + activity['start_date_local'])
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

        logging.info("Sleeping for 30 seconds")
        logging.info("---------------------------------------------------------------------------------------------------")
        sleep(30)

except Exception:
    logging.error(traceback.format_exc())
except (KeyboardInterrupt, SystemExit):
    logging.info("'Select Gear Bot' Stopped")
    logging.info("---------------------------------------------------------------------------------------------------")
    sys.exit()