# -*- coding: utf-8 -*-

import database as db

def test_insert_user_into_database():
    client = db.connect_to_db(2000)
    if client is None:
        assert True
        return
    db.clear_all_collections(client)
    my_user = { "name": "John",
              "address": "Highway 37", 
              "email": "john@bluewin.ch", 
              "mobile": "+41 79 123 45 99" 
              }
    db.insert_user(client, my_user)
    result = list(db.find_all_users(client))
    print(result)
    assert len(result) == 1
    assert result[0]["name"] == my_user['name']
    assert result[0]["address"] == my_user['address']
    assert result[0]["email"] == my_user['email']
    assert result[0]["mobile"] == my_user['mobile']

def test_insert_data_into_database():
    client = db.connect_to_db(2000)
    if client is None:
        assert True
        return
    db.clear_all_collections(client)
    my_data = { "station": "1234",
        "speed": "12.3", 
        "direction": "360°", 
        "ts": "xxx",
        "temp": "3.5"
        }
    db.insert_data(client, my_data)
    result = list(db.find_all_data(client))
    print(result)
    assert len(result) == 1
    assert result[0]["station"] == my_data['station']
    assert result[0]["speed"] == my_data['speed']
    assert result[0]["direction"] == my_data['direction']
    assert result[0]["ts"] == my_data['ts']
    assert result[0]["temp"] == my_data['temp']
