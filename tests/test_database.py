# -*- coding: utf-8 -*-
import pytest
from bson.objectid import ObjectId
from app import database as db
from app.models import (
    DataModel,
    StationModel,
    SubscriptionModel,
    ThresholdModel,
    UserModel,
)

@pytest.fixture(scope="function")
def test_db():
    client, db_instance = db.connect_to_db(2000, db_name="windseeker_test")
    db.clear_all_collections(db_instance)
    yield db_instance
    db.clear_all_collections(db_instance)
    client.close()


def create_test_subscription(station_id: int, station_name: str):
    return SubscriptionModel(id=station_id, name=station_name)

def create_test_user(username: str, station_1: int = 1234, station_2: int = 5678):
    return UserModel(
        username=username,
        name="John",
        address="Highway 37",
        email=f"{username}@bluewin.ch",
        mobile="+41 79 123 45 99",
        birthday="1986-11-21",
        password="123_Forever",
        subscriptions=[
            create_test_subscription(station_1, "dummy station 1"),
            create_test_subscription(station_2, "dummy station 2"),
        ],
    )

def create_test_station(station_id):
    return StationModel(
        id=station_id,
        name=f"dummy pytest station_{station_id}",
        subscribers=[],
    )

def create_test_threshold(username, station, threshold):
    return ThresholdModel(username=username, station=station, threshold=threshold)

def test_insert_user_into_database(test_db):
    user = create_test_user("Anna_Nalani")
    db.insert_user(test_db, user)
    result = list(db.find_all_users(test_db))

    assert len(result) == 1
    stored_user = result[0]
    assert stored_user["username"] == user.username
    assert stored_user["subscriptions"][0]["name"] == user.subscriptions[0].name

def test_insert_data_into_database(test_db):
    my_data = {
        "name": "Data from pytest",
        "station": 1234,
        "speed": 12.3,
        "direction": 360,
        "ts": "xxx",
        "temp": 3.5,
    }
    data = DataModel(**my_data)
    db.insert_data(test_db, data)
    result = list(db.find_all_data(test_db))

    assert len(result) == 1
    assert result[0]["station"] == my_data["station"]

def test_insert_station_into_database(test_db):
    station = create_test_station(1234)
    db.insert_station(test_db, station)
    result = list(db.find_all_stations(test_db))

    assert len(result) == 1
    assert result[0]["name"] == station.name

def test_add_user_to_existing_station_as_subscriber_by_id(test_db):
    user = create_test_user("Jonny_test")
    user_id = db.insert_user(test_db, user)
    db.insert_station(test_db, create_test_station(1234))
    db.insert_station(test_db, create_test_station(5678))

    user_obj = db.find_user_by_id(test_db, user_id)
    db.add_user_to_station_by_id(test_db, user_obj)

    result = db.find_station_id(test_db, 1234)
    assert len(result[0]["subscribers"]) == 1
    assert result[0]["subscribers"][0] == ObjectId(user_id)

def test_add_user_to_existing_station_as_subscriber_by_username(test_db):
    user = create_test_user("Ramon_by_pytest")
    db.insert_user(test_db, user)
    db.insert_station(test_db, create_test_station(1234))
    db.insert_station(test_db, create_test_station(5678))

    user_obj = db.find_user_by_username(test_db, user.username)
    db.add_user_to_station_by_username(test_db, user_obj)

    result = db.find_station_id(test_db, 1234)
    assert result[0]["subscribers"][0] == user.username

def test_add_user_to_new_station_as_subscriber(test_db):
    user = create_test_user("Baba_Test")
    db.insert_user(test_db, user)

    user_obj = db.find_user_by_username(test_db, user.username)
    db.add_user_to_station_by_username(test_db, user_obj)

    result = db.find_station_id(test_db, 1234)
    assert result[0]["subscribers"][0] == user.username

def test_threshold_usernames_per_station(test_db):
    db.insert_threshold(test_db, create_test_threshold("Baba_Test", 1234, 11.0))
    db.insert_threshold(test_db, create_test_threshold("Jonny_Test", 1234, 13.6))

    result = db.find_all_usernames_for_threshold_station(test_db, 1234, 13.6)
    usernames = [r[0] for r in result]

    assert "Baba_Test" in usernames
    assert "Jonny_Test" in usernames

def test_threshold_usernames_per_station_greater(test_db):
    db.insert_threshold(test_db, create_test_threshold("Baba_Test", 1234, 9.9))
    db.insert_threshold(test_db, create_test_threshold("Jonny_Test", 1234, 10.1))

    result = db.find_all_usernames_for_threshold_station(test_db, 1234, 10.0)
    usernames = [r[0] for r in result]

    assert "Baba_Test" in usernames
    assert "Jonny_Test" not in usernames
