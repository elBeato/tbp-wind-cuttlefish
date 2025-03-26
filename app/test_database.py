# -*- coding: utf-8 -*-

import database as db
from models import UserModel, DataModel, StationModel

def create_test_user():
    my_user = {
        "username": "Jonny B from pytest",
        "name": "John",
        "address": "Highway 37", 
        "email": "john@bluewin.ch", 
        "mobile": "+41 79 123 45 99",
        "birthday": "1986-11-21",
        "password": "123_Forever",
        "subscriptions": [1234, 5678]
        }
    return UserModel(**my_user)

def create_test_station(number):
    my_station = {
        "name": "dummy pytest station",
        "number": number,
        "subscribers": []
        }
    return StationModel(**my_station)

def test_insert_user_into_database():
    client = db.connect_to_db(2000)
    if client is None:
        assert False
        return
    db.clear_user_collection(client)
    user = create_test_user()
    db.insert_user(client, user.dict())
    result = list(db.find_all_users(client))
    print(result)
    assert len(result) == 1
    assert result[0]["name"] == user.name
    assert result[0]["address"] == user.address
    assert result[0]["email"] == user.email
    assert result[0]["mobile"] == user.mobile
    assert result[0]["birthday"] == user.birthday
    assert result[0]["password"] == user.password
    assert result[0]["subscriptions"] == user.subscriptions

def test_insert_data_into_database():
    client = db.connect_to_db(2000)
    if client is None:
        assert False
        return
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
    db.insert_data(client, data.dict())
    result = list(db.find_all_data(client))
    print(result)
    assert len(result) == 1
    assert result[0]["station"] == my_data['station']
    assert result[0]["speed"] == my_data['speed']
    assert result[0]["direction"] == my_data['direction']
    assert result[0]["ts"] == my_data['ts']
    assert result[0]["temp"] == my_data['temp']

def test_insert_station_into_database():
    client = db.connect_to_db(2000)
    if client is None:
        assert False
        return
    db.clear_station_collection(client)
    station = create_test_station(1234)
    db.insert_station(client, station.dict())
    result = list(db.find_all_stations(client))
    print(result)
    assert len(result) == 1
    assert result[0]["name"] == "dummy pytest station"
    assert result[0]["number"] == 1234
    assert result[0]["subscribers"] == []

def test_add_user_to_existing_station_as_subscriber_by_id():
    client = db.connect_to_db(2000)
    if client is None:
        assert False
        return
    db.clear_all_collections(client)

    user = create_test_user()
    user_id = db.insert_user(client, user.dict())
    station = create_test_station(1234)
    db.insert_station(client, station.dict())
    station = create_test_station(5678)
    db.insert_station(client, station.dict())
    user = db.find_user_by_id(client, user_id)
    db.add_user_to_station_by_id(client, user)
    result = db.find_station_number(client, 1234)
    print(result)
    assert len(result) == 1
    assert len(result[0]["subscribers"]) == 1
    assert result[0]["subscribers"][0] == user[0]['_id']

def test_add_user_to_existing_station_as_subscriber_by_username():
    client = db.connect_to_db(2000)
    if client is None:
        assert False
        return
    db.clear_all_collections(client)

    user = create_test_user()
    db.insert_user(client, user.dict())
    station = create_test_station(1234)
    db.insert_station(client, station.dict())
    station = create_test_station(5678)
    db.insert_station(client, station.dict())
    user = db.find_user_by_username(client, user.username)
    db.add_user_to_station_by_username(client, user)
    result = db.find_station_number(client, 1234)
    print(result)
    assert len(result) == 1
    assert len(result[0]["subscribers"]) == 1
    assert result[0]["subscribers"][0] == user[0]['username']

def test_add_user_to_new_station_as_subscriber():
    client = db.connect_to_db(2000)
    if client is None:
        assert False
        return
    db.clear_all_collections(client)

    user = create_test_user()
    db.insert_user(client, user.dict())

    user = db.find_user_by_username(client, user.username)
    db.add_user_to_station_by_username(client, user)
    result = db.find_station_number(client, 1234)
    print(result)
    assert len(result) == 1
    assert len(result[0]["subscribers"]) == 1
    assert result[0]["subscribers"][0] == user[0]['username']
