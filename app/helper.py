# -*- coding: utf-8 -*-
import os
import time
import requests
from functools import wraps
from flask import request, jsonify
import jwt
from bson import json_util
from requests import ConnectTimeout
from app import database as db
from app import windlogger as wl

def get_backup_dir() -> str:
    """
    Check for Docker environment by presence of a known env var or file
    """
    if os.path.exists("/.dockerenv") or os.environ.get("IN_DOCKER") == "1":
        return "/app/backup"
    return "../backup"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = payload["user_id"]  # optionally attach to request context
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(*args, **kwargs)

    return decorated


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
    # Ensure backup directory exists
    os.makedirs("backup", exist_ok=True)

    # Connect to MongoDB
    client, db_instance = db.connect_to_db()

    # Fetch all documents
    users = list(db_instance.Users.find())
    stations = list(db_instance.Stations.find())
    thresholds = list(db_instance.Thresholds.find())
    windguru_stations = list(db_instance.WindguruStations.find())
    client.close()

    # Save to a JSON file
    backup_dir = get_backup_dir()
    os.makedirs(backup_dir, exist_ok=True)
    with open(os.path.join(backup_dir, "users_backup.json"), "w", encoding="utf-8") as file:
        file.write(json_util.dumps(users, indent=4))
    with open(os.path.join(backup_dir, "stations_backup.json"), "w", encoding="utf-8") as file:
        file.write(json_util.dumps(stations, indent=4))
    with open(os.path.join(backup_dir, "thresholds_backup.json"), "w", encoding="utf-8") as file:
        file.write(json_util.dumps(thresholds, indent=4))
    with open(
            os.path.join(backup_dir, "windguru_stations_backup.json"),
            "w",
            encoding="utf-8"
    ) as file:
        file.write(json_util.dumps(windguru_stations, indent=4))

    wl.logger.info("Collection exported to \\backup\\users_backup.json")
    wl.logger.info("Collection exported to \\backup\\stations_backup.json")
    wl.logger.info("Collection exported to \\backup\\thresholds_backup.json")
    wl.logger.info("Collection exported to \\backup\\windguru_stations_backup.json")
    return True
