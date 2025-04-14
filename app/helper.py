# -*- coding: utf-8 -*-
import json
import time
import requests
from requests import ConnectTimeout
from app import database as db
from app import windlogger as wl

# Using a closure function with enclosed state
def counter():
    count = 0  # Initial counter value

    def increment(reset=False):
        nonlocal count  # Use nonlocal to modify the outer variable
        if reset:
            count = 0
        else:
            count += 1
        return count

    return increment

def check_response_contains_param(response, station_id, log_result = True):
    try:
        if response['wind_avg'] is not None and response['wind_direction'] is not None:
            return True
    except Exception as ex:
        if log_result:
            wl.logger.warning(f'[{time.strftime("%H:%M:%S")}]: ' +
                              f'Station = [{station_id}] response doesnt contains '+
                              f'average windspeed and wind direction - {ex}')
    return False

def get_next_station_ids():
    client, db_instance = db.connect_to_db(2000)
    station_entries = db.find_all_stations(db_instance)
    station_ids = []
    for station in station_entries:
        station_ids.append(station['id'])
    client.close()
    return station_ids

def fetch_data_from_windguru(url1, url2, station_id):
    try:
        headers = {'Referer': f"{url1}{station_id}"}
        req = requests.get(f"{url2}{station_id}", headers=headers, timeout=10)
    except ConnectTimeout as con_ex:
        time.sleep(30) # sleep for 30 seconds
        wl.logger.info(f'[helper.py]: Fetch data from station[{station_id}] '
                       f'again with timeout=20sec - Error:{con_ex}')
        headers = {'Referer': f"{url1}{station_id}"}
        req = requests.get(f"{url2}{station_id}", headers=headers, timeout=20)
    return req

def store_collections_local_on_host() -> bool:
    # Connect to MongoDB
    client, db_instance = db.connect_to_db()

    # Fetch all documents
    user = list(db.connect_to_user_collection(db_instance).find())
    station = list(db.connect_to_station_collection(db_instance).find())
    threshold = list(db.connect_to_threshold_collection(db_instance).find())
    client.close()

    # Convert ObjectId to string (if needed)
    for doc in user:
        doc["_id"] = str(doc["_id"])

    for doc in station:
        doc["_id"] = str(doc["_id"])

    for doc in threshold:
        doc["_id"] = str(doc["_id"])

    # Save to a JSON file
    with open("backup/user_backup.json", "w", encoding="utf-8") as file:
        json.dump(user, file, indent=4)
    with open("backup/station_backup.json", "w", encoding="utf-8") as file:
        json.dump(station, file, indent=4)
    with open("backup/threshold_backup.json", "w", encoding="utf-8") as file:
        json.dump(threshold, file, indent=4)

    wl.logger.info("Collection exported to user_backup.json")
    wl.logger.info("Collection exported to station_backup.json")
    wl.logger.info("Collection exported to threshold_backup.json")
    return True
