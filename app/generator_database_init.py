# -*- coding: utf-8 -*-
from pymongo import MongoClient
import database as db
from tests.test_database import create_test_user, create_test_station, create_test_threshold

def init() -> MongoClient:
    client = db.connect_to_db()
    db.clear_all_collections(client)
    basic_database_init(client)
    return client

def basic_database_init(client):
    users = [
        create_test_user("Anna_username", 1234, 5931),
        create_test_user("Nerea_username", 123, 2736),
        create_test_user("Rene_username", 5931, 2736),
        create_test_user("Kevin_username", 55, 1282436)
    ]

    stations = [
        create_test_station(1234),
        create_test_station(5931),
        create_test_station(2736),
        create_test_station(55),
        create_test_station(1282436),
    ]

    thresholds = [
        create_test_threshold('Anna_username', 1234, 1.5),
        create_test_threshold('Anna_username', 5931, 10.6),
        create_test_threshold('Nerea_username', 1234, 2.5),
        create_test_threshold('Nerea_username', 2736, 11.6),
        create_test_threshold('Rene_username', 5931, 3.5),
        create_test_threshold('Rene_username', 2736, 12.6),
        create_test_threshold('Kevin_username', 55, 4.5),
        create_test_threshold('Kevin_username', 1282436, 13.6),
    ]

    _ = [db.insert_user(client, user) for user in users]
    _ = [db.insert_station(client, station) for station in stations]
    _ = [db.insert_threshold(client, ts) for ts in thresholds]

init()
