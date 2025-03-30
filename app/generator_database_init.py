# -*- coding: utf-8 -*-
from pymongo import MongoClient
from test_database import create_test_user, create_test_station, create_test_threshold
import database as db

def init() -> MongoClient:
    client = db.connect_to_db()
    db.clear_all_collections(client)
    basic_database_init(client)
    return client

def basic_database_init(client):
    users = [
        create_test_user("Anna_username", 123, 456),
        create_test_user("Nerea_username", 123, 789),
        create_test_user("Rene_username", 456, 789),
        create_test_user("Kevin_username", 55, 66)
    ]

    stations = [
        create_test_station(123),
        create_test_station(456),
        create_test_station(789),
        create_test_station(55),
        create_test_station(66),
    ]

    thresholds = [
        create_test_threshold('Anna_username', 123, 1.5),
        create_test_threshold('Anna_username', 456, 10.6),
        create_test_threshold('Nerea_username', 123, 2.5),
        create_test_threshold('Nerea_username', 789, 11.6),
        create_test_threshold('Rene_username', 456, 3.5),
        create_test_threshold('Rene_username', 789, 12.6),
        create_test_threshold('Kevin_username', 55, 4.5),
        create_test_threshold('Kevin_username', 66, 13.6),
    ]

    _ = [db.insert_user(client, user.dict()) for user in users]
    _ = [db.insert_station(client, station.dict()) for station in stations]
    _ = [db.insert_threshold(client, ts.dict()) for ts in thresholds]

init()
