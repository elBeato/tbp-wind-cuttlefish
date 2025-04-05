# -*- coding: utf-8 -*-
import os
import pytest
from app import database as db
from bson.objectid import ObjectId
from app.models import UserModel, DataModel, StationModel, ThresholdModel, SubscriptionModel

@pytest.fixture
def test_db_param():
    return "locally" if "GITHUB_ACTIONS" not in os.environ else "github"

def create_test_subscription(station_id: int, station_name: str):
    my_sub = {"id": station_id, "name": station_name}
    return SubscriptionModel(**my_sub)

def create_test_user(username: str, station_1: int = 1234, station_2: int = 5678):
    my_user = {
        "username": username,
        "name": "John",
        "address": "Highway 37", 
        "email": f"{username}@bluewin.ch", 
        "mobile": "+41 79 123 45 99",
        "birthday": "1986-11-21",
        "password": "123_Forever",
        "subscriptions": [ 
            create_test_subscription(station_1, "dummy station 1"),
            create_test_subscription(station_2, "dummy station 2")
            ]
        }
    return UserModel(**my_user)

def create_test_station(number):
    my_station = {
        "name": f'dummy pytest station_{number}',
        "number": number,
        "subscribers": []
        }
    return StationModel(**my_station)

def create_test_threshold(username, station, threshold):
    my_threshold = {
        "username": username,
        "station": station,
        "threshold": threshold
        }
    return ThresholdModel(**my_threshold)

def test_insert_user_into_database(test_db_param):
    print(f"Test with param: {test_db_param}")
    assert test_db_param in ["locally", "github"]

    if test_db_param == "github":
        assert True
        return

    client = db.connect_to_db(2000)
    db.clear_user_collection(client)
    user = create_test_user("Anna_Nalani")
    db.insert_user(client, user)
    result = list(db.find_all_users(client))
    print(result)
    assert len(result) == 1
    assert result[0]["name"] == user.name
    assert result[0]["address"] == user.address
    assert result[0]["email"] == user.email
    assert result[0]["mobile"] == user.mobile
    assert result[0]["birthday"] == user.birthday
    assert result[0]["password"] == user.password
    assert result[0]["subscriptions"][0]['name'] == user.subscriptions[0].name
    assert result[0]["subscriptions"][1]['name'] == user.subscriptions[1].name
    assert result[0]["subscriptions"][0]['id'] == user.subscriptions[0].id
    assert result[0]["subscriptions"][1]['id'] == user.subscriptions[1].id

def test_insert_data_into_database(test_db_param):
    print(f"Running test with param: {test_db_param}")
    assert test_db_param in ["locally", "github"]

    if test_db_param == "github":
        assert True
        return

    client = db.connect_to_db(2000)
    db.clear_data_collection(client)
    my_data = {
        "name":"Data from pytest",
        "station": 1234,
        "speed": 12.3, 
        "direction": 360, 
        "ts": "xxx",
        "temp": 3.5
        }
    data = DataModel(**my_data)
    db.insert_data(client, data)
    result = list(db.find_all_data(client))
    print(result)
    assert len(result) == 1
    assert result[0]["station"] == my_data['station']
    assert result[0]["speed"] == my_data['speed']
    assert result[0]["direction"] == my_data['direction']
    assert result[0]["ts"] == my_data['ts']
    assert result[0]["temp"] == my_data['temp']

def test_insert_station_into_database(test_db_param):
    print(f"Test with param: {test_db_param}")
    assert test_db_param in ["locally", "github"]

    if test_db_param == "github":
        assert True
        return

    client = db.connect_to_db(2000)
    db.clear_station_collection(client)
    station = create_test_station(1234)
    db.insert_station(client, station)
    result = list(db.find_all_stations(client))
    print(result)
    assert len(result) == 1
    assert result[0]["name"] == f"dummy pytest station_{1234}"
    assert result[0]["number"] == 1234
    assert result[0]["subscribers"] == []

def test_add_user_to_existing_station_as_subscriber_by_id(test_db_param):
    print(f"Test with param: {test_db_param}")
    assert test_db_param in ["locally", "github"]

    if test_db_param == "github":
        assert True
        return

    client = db.connect_to_db(2000)
    db.clear_all_collections(client)

    user = create_test_user("Jonny_test")
    user_id = db.insert_user(client, user)
    station = create_test_station(1234)
    db.insert_station(client, station)
    station = create_test_station(5678)
    db.insert_station(client, station)
    user = db.find_user_by_id(client, user_id)
    db.add_user_to_station_by_id(client, user)
    result = db.find_station_number(client, 1234)
    print(result)
    assert len(result) == 1
    assert len(result[0]["subscribers"]) == 1
    assert result[0]["subscribers"][0] == ObjectId(user_id)

def test_add_user_to_existing_station_as_subscriber_by_username(test_db_param):
    print(f"Test with param: {test_db_param}")
    assert test_db_param in ["locally", "github"]

    if test_db_param == "github":
        assert True
        return

    client = db.connect_to_db(2000)
    db.clear_all_collections(client)

    user = create_test_user("Ramon_by_pytest")
    db.insert_user(client, user)
    station = create_test_station(1234)
    db.insert_station(client, station)
    station = create_test_station(5678)
    db.insert_station(client, station)
    user = db.find_user_by_username(client, user.username)
    db.add_user_to_station_by_username(client, user)
    result = db.find_station_number(client, 1234)
    print(result)
    assert len(result) == 1
    assert len(result[0]["subscribers"]) == 1
    assert result[0]["subscribers"][0] == user.username

def test_add_user_to_new_station_as_subscriber(test_db_param):
    print(f"Test with param: {test_db_param}")
    assert test_db_param in ["locally", "github"]

    if test_db_param == "github":
        assert True
        return

    client = db.connect_to_db(2000)
    db.clear_all_collections(client)

    user = create_test_user("Baba_Test")
    db.insert_user(client, user)

    user = db.find_user_by_username(client, user.username)
    db.add_user_to_station_by_username(client, user)
    result = db.find_station_number(client, 1234)
    print(result)
    assert len(result) == 1
    assert len(result[0]["subscribers"]) == 1
    assert result[0]["subscribers"][0] == user.username

def test_threshold_usernames_per_station(test_db_param):
    print(f"Test with param: {test_db_param}")
    assert test_db_param in ["locally", "github"]

    if test_db_param == "github":
        assert True
        return
    # Arrange
    # Connect to threshold collection
    client = db.connect_to_db(2000)
    db.clear_threshold_collection(client)
    # insert first document
    threshold = create_test_threshold("Baba_Test", 1234, 11.0)
    db.insert_threshold(client, threshold)
    # insert second document
    threshold = create_test_threshold("Jonny_Test", 1234, 13.6)
    db.insert_threshold(client, threshold)

    # Act
    result = db.find_all_usernames_for_threshold_station(client, 1234, 13.6)

    print(result)
    assert len(result) == 2
    assert result[0][0] == "Baba_Test"
    assert result[1][0] == "Jonny_Test"

def test_threshold_usernames_per_station_greater(test_db_param):
    print(f"Test with param: {test_db_param}")
    assert test_db_param in ["locally", "github"]

    if test_db_param == "github":
        assert True
        return
    # Arrange
    # Connect to threshold collection
    client = db.connect_to_db(2000)
    db.clear_threshold_collection(client)
    # insert first document
    threshold = create_test_threshold("Baba_Test", 1234, 9.9)
    db.insert_threshold(client, threshold)
    # insert second document
    threshold = create_test_threshold("Jonny_Test", 1234, 10.1)
    db.insert_threshold(client, threshold)

    # Act
    result = db.find_all_usernames_for_threshold_station(client, 1234, 10.0)

    print(result)
    assert len(result) == 1
    assert result[0][0] == "Baba_Test"
