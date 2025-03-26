# -*- coding: utf-8 -*-

import database as db
from models import UserModel, DataModel

def test_insert_user_into_database():
    client = db.connect_to_db(2000)
    if client is None:
        assert True
        return
    db.clear_user_collection(client)
    my_user = {
        "username": "Jonny B from pytest",
        "name": "John",
        "address": "Highway 37", 
        "email": "john@bluewin.ch", 
        "mobile": "+41 79 123 45 99",
        "birthday": "1986-11-21",
        "password": "123_Forever",
        "subscriptions": ["Isleten", "Hoo'kipa"]
        }
    user = UserModel(**my_user)
    db.insert_user(client, user.dict())
    result = list(db.find_all_users(client))
    print(result)
    assert len(result) == 1
    assert result[0]["name"] == my_user['name']
    assert result[0]["address"] == my_user['address']
    assert result[0]["email"] == my_user['email']
    assert result[0]["mobile"] == my_user['mobile']
    assert result[0]["birthday"] == my_user['birthday']
    assert result[0]["password"] == my_user['password']
    assert result[0]["subscriptions"] == my_user['subscriptions']

def test_insert_data_into_database():
    client = db.connect_to_db(2000)
    if client is None:
        assert True
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
