# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 10:45:13 2025

@author: fub
"""
from models import UserModel, DataModel, StationModel
import pymongo
from bson.objectid import ObjectId
import configuration as config
import windlogger as logger

def add_user_to_station(client, user, identification):
    for station_number in user['subscriptions']:
        if find_station_number(client, station_number) is None:
            my_list = []
            my_list.append(identification)
            my_station = {
                "name": "placeholder",
                "number": station_number,
                "subscribers": my_list
                }
            station = StationModel(**my_station)
            insert_station(client, station.dict())
        else:
            connect_to_station_collection(client).update_one(
                {"number": station_number},
                {"$push": {"subscribers": identification}}
            )

def connect_to_db(timeout_ms = 5000):
    """Connects to MongoDB and checks if the connection is healthy."""
    try:
        host = config.get_config_value("mongohost")
        port = config.get_config_value("mongoport")
        client = pymongo.MongoClient(f"mongodb://root:supersecurepassword@{host}:{port}/",
                                     timeoutMS=timeout_ms)

        # Ping the database
        client.admin.command("ping")

        print("✅ MongoDB connection is healthy.")
        return client  # Return the client if connection is successful

    except pymongo.errors.ConnectionFailure as ex:
        print(f"❌ MongoDB connection failed: {ex}")
        return None  # Return None if connection fails

def get_database_name():
    return config.get_config_value('databaseName')

def get_user_collection():
    return config.get_config_value('userCollection')

def get_data_collection():
    return config.get_config_value('dataCollection')

def get_station_collection():
    return config.get_config_value('stationCollection')

def connect_to_user_collection(client):
    database = client[get_database_name()]
    return database[get_user_collection()]

def connect_to_data_collection(client):
    database = client[get_database_name()]
    return database[get_data_collection()]

def connect_to_station_collection(client):
    database = client[get_database_name()]
    collection = database[get_station_collection()]
    collection.create_index("number", unique=True) # Ensure uniqueness of the 'number' field
    print("Unique index on 'number' field created.")
    return collection

def insert_user(client, user: UserModel):
    try:
        result = connect_to_user_collection(client).insert_one(user)
        return str(result.inserted_id)
    except Exception as ex:
        logger.logging.error(f'Method: insert_user(client, user): {ex}')
    return None

def insert_data(client, data: DataModel):
    connect_to_data_collection(client).insert_one(data)

def insert_station(client, station: StationModel):
    connect_to_station_collection(client).insert_one(station)

def add_user_to_station_by_id(client, users: UserModel):
    for user in users:
        identification = user['_id']
        add_user_to_station(client, user, identification)

def add_user_to_station_by_username(client, users: UserModel):
    for user in users:
        identification = user['username']
        add_user_to_station(client, user, identification)

def find_all_users(client):
    return list(connect_to_user_collection(client).find())

def find_user_by_id(client, user_id):
    return list(connect_to_user_collection(client).find({"_id": ObjectId(user_id)}))

def find_user_by_username(client, username):
    return list(connect_to_user_collection(client).find({"username": username}))

def find_all_data(client):
    return list(connect_to_data_collection(client).find())

def find_all_stations(client):
    return list(connect_to_station_collection(client).find())

def find_station_number(client, number):
    result = list(connect_to_station_collection(client).find({"number": number}))
    if len(result) > 1:
        logger.logging.critical('Method: find_station_number(client, number): ' +
                                f'More then one occurence of the station {number}')
    else:
        if len(result) == 1:
            return result
    return None

def clear_user_collection(client):
    x = connect_to_user_collection(client).delete_many({})
    return x.deleted_count

def clear_data_collection(client):
    x = connect_to_data_collection(client).delete_many({})
    return x.deleted_count

def clear_station_collection(client):
    x = connect_to_station_collection(client).delete_many({})
    return x.deleted_count

def clear_all_collections(client):
    count = clear_user_collection(client)
    count += clear_data_collection(client)
    count += clear_station_collection(client)
    return count
