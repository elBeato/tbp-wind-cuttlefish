# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
import os
import pytest
from app import startup
from app import helper as hp
from app import database as db
from tests.test_database import create_test_user, create_test_threshold, test_db

@pytest.fixture
def test_param():
    return "local" if "GITHUB_ACTIONS" not in os.environ else "github"

def test_call_windguru_api():
    station_ids = [2736, 5931]
    count_func = hp.counter()
    req = startup.windguru_api_call(
        'https://www.windguru.cz/station/', 
        'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=', 
        station_ids,
        count_func,
        30,
        90
    )
    expected = "https://www.windguru.cz/int/iapi.php?" \
        "q=station_data_current&id_station=" + str(station_ids[1])

    assert req.url == expected
    assert req.status_code == 200
    assert req.encoding == 'utf-8'
    assert req.content is not None
    assert req.content != {}

def test_call_windguru_api_types():
    station_ids = [2736, 5931]  # Ho'okipa Maui
    count_func = hp.counter()
    req = startup.windguru_api_call(
        'https://www.windguru.cz/station/', 
        'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=', 
        station_ids,
        count_func,
        30,
        90
    )
    expected = "https://www.windguru.cz/int/iapi.php?" \
        "q=station_data_current&id_station=" + str(station_ids[1])

    response = req.json()
    wind_avg = response['wind_avg']
    wind_max = response['wind_max']
    wind_min = response['wind_min']
    wind_direction = response['wind_direction']
    temperature = response['temperature']
    datetime = response['datetime']
    unixtime = response['unixtime']

    assert req.url == expected
    assert isinstance(wind_avg, (int, float))
    assert isinstance(wind_max, (int, float))
    assert isinstance(wind_min, (int, float))
    assert isinstance(wind_direction, (int, float))
    assert isinstance(temperature, (int, float))
    assert isinstance(datetime, str)
    assert isinstance(unixtime, int)

def test_call_windguru_api_values():
    station_ids = [2736, 5931]  # Ho'okipa Maui
    count_func = hp.counter()
    req = startup.windguru_api_call(
        'https://www.windguru.cz/station/', 
        'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=', 
        station_ids,
        count_func,
        30,
        90
    )
    expected = "https://www.windguru.cz/int/iapi.php?" \
        "q=station_data_current&id_station=" + str(station_ids[1])

    response = req.json()
    wind_avg = response['wind_avg']
    wind_max = response['wind_max']
    wind_min = response['wind_min']
    wind_direction = response['wind_direction']
    temperature = response['temperature']
    datetime = response['datetime']
    unixtime = response['unixtime']

    assert req.url == expected
    assert response is not None
    assert wind_avg >= 0.0
    assert wind_max >= 0.0
    assert wind_min >= 0.0
    assert wind_direction >= 0
    assert temperature >= -80.0
    assert unixtime >= 0

    assert isinstance(wind_avg, (int, float))
    assert isinstance(wind_max, (int, float))
    assert isinstance(wind_min, (int, float))
    assert isinstance(wind_direction, (int, float))
    assert isinstance(temperature, (int, float))
    assert isinstance(datetime, str)
    assert isinstance(unixtime, int)

def test_call_windguru_api_print_values():
    station_ids = [2736, 5931]  # Ho'okipa Maui
    count_func = hp.counter()
    req = startup.windguru_api_call(
        'https://www.windguru.cz/station/', 
        'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=', 
        station_ids,
        count_func,
        30,
        90
    )
    expected = "https://www.windguru.cz/int/iapi.php?" \
        "q=station_data_current&id_station=" + str(station_ids[1])

    response = req.json()
    wind_avg = response['wind_avg']
    wind_max = response['wind_max']
    wind_min = response['wind_min']
    wind_direction = response['wind_direction']
    temperature = response['temperature']
    datetime = response['datetime']
    unixtime = response['unixtime']

    assert req.url == expected

    print(f'wind_avg: {wind_avg}')
    print(f'wind_max: {wind_max}')
    print(f'wind_min: {wind_min}')
    print(f'wind_direction: {wind_direction}')
    print(f'temperature: {temperature}')
    print(f'datetime: {datetime}')
    print(f'unixtime: {unixtime}')

def test_fetch_all_emails(test_param, test_db):
    print(f"Running test with param: {test_param}")
    assert test_param in ["local", "github"]

    if test_param == "github":
        assert True
        return

    # Arrange
    user1 = create_test_user("Jonny_startup_test")
    user2 = create_test_user("Rene_startup_test")
    user3 = create_test_user("Bubu_startup_test")
    db.insert_user(test_db, user1)
    db.insert_user(test_db, user2)
    db.insert_user(test_db, user3)

    thres1 = create_test_threshold(user1.username, 1, 1.2)
    thres2 = create_test_threshold(user2.username, 2, 2.4)
    thres3 = create_test_threshold(user3.username, 3, 3.6)
    db.insert_threshold(test_db, thres1)
    db.insert_threshold(test_db, thres2)
    db.insert_threshold(test_db, thres3)

    email_list1 = startup.fetch_email_addresses_for_station(1, 3.6, "windseeker_test")
    email_list2 = startup.fetch_email_addresses_for_station(2, 3.6, "windseeker_test")
    email_list3 = startup.fetch_email_addresses_for_station(3, 3.6, "windseeker_test")

    assert len(email_list1) == 1
    assert len(email_list2) == 1
    assert len(email_list3) == 1
    assert email_list1[0] == user1.email
    assert email_list2[0] == user2.email
    assert email_list3[0] == user3.email

def test_fetch_all_emails_complex_subscriptions(test_param):
    print(f"Running test with param: {test_param}")
    assert test_param in ["local", "github"]

    if test_param == "github":
        assert True
        return

    client, db_instance = db.connect_to_db(timeout_ms=2000, db_name='windseeker_test')
    db.clear_all_collections(db_instance)

    # Arrange
    user1 = create_test_user("Jonny_startup_test")
    user2 = create_test_user("Rene_startup_test")
    user3 = create_test_user("Bubu_startup_test")
    db.insert_user(db_instance, user1)
    db.insert_user(db_instance, user2)
    db.insert_user(db_instance, user3)

    thres1 = create_test_threshold(user1.username, 1, 1.2)
    thres2 = create_test_threshold(user1.username, 2, 2.4)
    thres3 = create_test_threshold(user2.username, 2, 3.6)
    thres4 = create_test_threshold(user1.username, 3, 4.8)
    thres5 = create_test_threshold(user2.username, 3, 5.9)
    thres6 = create_test_threshold(user3.username, 3, 5.9)
    db.insert_threshold(db_instance, thres1)
    db.insert_threshold(db_instance, thres2)
    db.insert_threshold(db_instance, thres3)
    db.insert_threshold(db_instance, thres4)
    db.insert_threshold(db_instance, thres5)
    db.insert_threshold(db_instance, thres6)

    email_list1 = startup.fetch_email_addresses_for_station(1, 5.9, "windseeker_test")
    email_list2 = startup.fetch_email_addresses_for_station(2, 5.9, "windseeker_test")
    email_list3 = startup.fetch_email_addresses_for_station(3, 5.9, "windseeker_test")

    assert len(email_list1) == 1
    assert len(email_list2) == 2
    assert len(email_list3) == 3
    assert (user1.email in email_list1) is True
    assert (user1.email in email_list2) is True
    assert (user1.email in email_list3) is True

    assert (user2.email in email_list1) is False
    assert (user2.email in email_list2) is True
    assert (user2.email in email_list3) is True

    assert (user3.email in email_list1) is False
    assert (user3.email in email_list2) is False
    assert (user3.email in email_list3) is True
    client.close()

def test_fetch_all_emails_current_wind_speed(test_param):
    print(f"Running test with param: {test_param}")
    assert test_param in ["local", "github"]

    if test_param == "github":
        assert True
        return

    client, db_instance = db.connect_to_db(timeout_ms=2000, db_name='windseeker_test')
    db.clear_all_collections(db_instance)
    # Arrange
    user1 = create_test_user("Jonny_startup_test")
    user2 = create_test_user("Rene_startup_test")
    db.insert_user(db_instance, user1)
    db.insert_user(db_instance, user2)

    # Station 1
    thres1 = create_test_threshold(user1.username, 1, 1.5)
    thres2 = create_test_threshold(user2.username, 1, 1.6)
    # Station 2
    thres3 = create_test_threshold(user1.username, 2, 2.5)
    thres4 = create_test_threshold(user2.username, 2, 2.6)
    # Station 3
    thres5 = create_test_threshold(user1.username, 3, 3.5)
    thres6 = create_test_threshold(user2.username, 3, 3.6)

    # Act
    db.insert_threshold(db_instance, thres1)
    db.insert_threshold(db_instance, thres2)
    db.insert_threshold(db_instance, thres3)
    db.insert_threshold(db_instance, thres4)
    db.insert_threshold(db_instance, thres5)
    db.insert_threshold(db_instance, thres6)

    email_list1 = startup.fetch_email_addresses_for_station(1, 1.4, "windseeker_test")
    email_list2 = startup.fetch_email_addresses_for_station(2, 2.5, "windseeker_test")
    email_list3 = startup.fetch_email_addresses_for_station(3, 3.6, "windseeker_test")

    # Assert
    assert len(email_list1) == 0
    assert len(email_list2) == 1
    assert len(email_list3) == 2

    assert (user1.email in email_list1) is False
    assert (user2.email in email_list1) is False

    assert (user1.email in email_list2) is True
    assert (user2.email in email_list2) is False

    assert (user1.email in email_list3) is True
    assert (user2.email in email_list3) is True
    db.clear_all_collections(db_instance)
    client.close()
