import os
import time
import json
import schedule
from app import configuration as config
from app import windlogger as wl
from app import database as db
from app.models import WindguruStationModel
from app.helper import fetch_data_from_windguru, check_response_contains_param

def get_file_path(file):
    # Get the current directory of the running file
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, 'backup', file)

def find_live_stations(response, n):
    if check_response_contains_param(response, n, False):
        return True
    return False

def find_offline_stations(response, n):
    if not check_response_contains_param(response, n, False):
        return True
    return False

def find_stations(station_types = find_live_stations):
    url_1 = config.get_config_value('url1')
    url_2 = config.get_config_value('url2')
    min_station = int(config.get_config_value('MIN_STATION_NUMBER'))
    max_station = int(config.get_config_value('MAX_STATION_NUMBER'))
    stations_ids = []
    for n in range(min_station, max_station):
        try:
            req = fetch_data_from_windguru(url_1, url_2, n)
            response = req.json()
            if station_types(response, n):
                stations_ids.append(n)
        except Exception as ex:
            wl.logger.info(f'[find_stations]: Error station[{n}] ' +
                           f'while fetching data from: {url_2} - {ex}')
    return stations_ids

def write_json_file_into_db():
    client = db.connect_to_db()
    # Get the current directory of the running file
    file = 'online_stations.json'
    file_path = get_file_path(file)
    with open(file_path, 'r', encoding='utf-8') as json_file:
        online_stations = json.load(json_file)
    for i, station in enumerate(online_stations):
        curr_station = WindguruStationModel(**station)
        curr_station.online = True
        online_stations[i] = curr_station
    cleared_docs = db.clear_windguru_station_collection(client)
    inserted_docs = db.insert_windguru_station(client, online_stations)
    wl.logger.info(f'[write_json_file_into_db]: {cleared_docs} stations deleted, ' +
                   '{inserted_docs} stations inserted' +
                   f'Difference: {inserted_docs - cleared_docs} new stations')

def merge_station_list_with_online_stations(live_stations: list[int]):
    # Get the current directory of the running file
    file = 'station_list.json'
    file_path = get_file_path(file)
    with open(file_path, 'r', encoding='utf-8') as json_file:
        scraped_stations = json.load(json_file)
    dict_stations = dict(enumerate(scraped_stations, start=1))
    # Filter the dictionary to only include keys from the list
    filtered_dict = {key: dict_stations[key] for key in live_stations if key in dict_stations}
    for key, value in filtered_dict.items():
        assert key == value['id'], f"Key {key} does not match id {value['id']}"
    return list(filtered_dict.values())

def read_live_stations_and_store_into_db():
    data = find_stations(find_live_stations)
    filtered_stations = merge_station_list_with_online_stations(data)
    file = 'online_stations.json'
    file_path = get_file_path(file)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(filtered_stations, json_file, ensure_ascii=False, indent=2)
    write_json_file_into_db()

def job():
    wl.logger.info("[Scheduler]: Starting station scraping job...")
    read_live_stations_and_store_into_db()
    wl.logger.info("[Scheduler]: Finished station scraping job.")

if __name__ == '__main__':
    os.makedirs('backup', exist_ok=True)

    # Schedule it once daily at 00:30 AM
    schedule.every().day.at("00:30").do(job)

    wl.logger.info("[Scheduler]: Job scheduled for 00:30 daily.")

    # Run the scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # check every minute
