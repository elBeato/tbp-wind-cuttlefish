# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 10:45:13 2025

@author: fub
"""
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from app import configuration as config
from app import windlogger as wl
from app.models import UserModel, DataModel, StationModel, ThresholdModel, WindguruStationModel

def add_user_to_station(client: MongoClient, user: UserModel, identification):
    for station in user.subscriptions:
        if find_station_id(client, station.id) is None:
            my_list = [identification]
            my_station = {
                "name": station.name,
                "id": station.id,
                "subscribers": my_list
            }
            station = StationModel(**my_station)
            insert_station(client, station)
        else:
            connect_to_station_collection(client).update_one(
                {"id": station.id},
                {"$push": {"subscribers": identification}}
            )


def connect_to_db(timeout_ms=5000):
    """Connects to MongoDB and checks if the connection is healthy."""
    try:
        host = config.get_config_value("MONGO_HOST")
        port = config.get_config_value("MONGO_PORT")
        user = config.get_config_value("MONGO_USERNAME")
        password = config.get_config_value("MONGO_PASSWORD")
        client = MongoClient(f"mongodb://{user}:{password}@{host}:{port}/",
                             timeoutMS=timeout_ms)
        # Ping the database
        client.admin.command("ping")

        wl.logger.info("MongoDB connection is healthy.")
        return client  # Return the client if connection is successful

    except errors.ConnectionFailure as ex:
        string = 'MongoDB connection failed: %s', str(ex)
        wl.logger.error(string)
        return None  # Return None if connection fails


def get_database_name():
    return config.get_config_value('databaseName')

def get_windguru_station_collection():
    return config.get_config_value('windguruStationCollection')

def get_user_collection():
    return config.get_config_value('userCollection')


def get_data_collection():
    return config.get_config_value('dataCollection')


def get_station_collection():
    return config.get_config_value('stationCollection')


def get_threshold_collection():
    return config.get_config_value('thresholdCollection')

def connect_to_windguru_station_collection(client: MongoClient):
    database = client[get_database_name()]
    collection = database[get_windguru_station_collection()]
    # Ensure uniqueness of the 'id' field
    collection.create_index("id", unique=True)
    return database[get_windguru_station_collection()]

def connect_to_user_collection(client: MongoClient):
    database = client[get_database_name()]
    collection = database[get_user_collection()]
    # Ensure uniqueness of the 'id' field
    collection.create_index("username", unique=True)
    return database[get_user_collection()]


def connect_to_data_collection(client: MongoClient):
    database = client[get_database_name()]
    return database[get_data_collection()]


def connect_to_station_collection(client: MongoClient):
    database = client[get_database_name()]
    collection = database[get_station_collection()]
    # Ensure uniqueness of the 'id' field
    collection.create_index("id", unique=True)
    return collection


def connect_to_threshold_collection(client: MongoClient):
    database = client[get_database_name()]
    collection = database[get_threshold_collection()]
    # Create the compound unique index on 'username' and 'station'
    collection.create_index(["username", "station"], unique=True)
    return collection


def insert_user(client: MongoClient, user: UserModel):
    try:
        user.hash_user_password()
        result = connect_to_user_collection(client).insert_one(user.model_dump())
        return str(result.inserted_id)
    except Exception as ex:
        wl.logging.error(f'Method: insert_user(client, user): {ex}')
    return None


def insert_data(client: MongoClient, data: DataModel):
    connect_to_data_collection(client).insert_one(data.model_dump())


def insert_station(client: MongoClient, station: StationModel):
    connect_to_station_collection(client).insert_one(station.model_dump())


def insert_threshold(client: MongoClient, threshold: ThresholdModel):
    connect_to_threshold_collection(client).insert_one(threshold.model_dump())

def insert_windguru_station(client: MongoClient, windguru_stations: list[WindguruStationModel]):
    docs = [station.model_dump(by_alias=True) for station in windguru_stations]
    result = connect_to_windguru_station_collection(client).insert_many(docs)
    return len(result.inserted_ids)

def add_user_to_station_by_id(client: MongoClient, user):
    identification = user['_id']
    add_user_to_station(client, UserModel(**user), identification)


def add_user_to_station_by_username(client: MongoClient, user: UserModel):
    identification = user.username
    add_user_to_station(client, user, identification)


def find_all_users(client: MongoClient):
    return list(connect_to_user_collection(client).find())


def find_all_windguru_stations(client: MongoClient):
    return list(connect_to_windguru_station_collection(client).find())

def find_user_by_id(client: MongoClient, user_id):
    user_data = connect_to_user_collection(client).find_one({"_id": ObjectId(user_id)})
    if user_data is None:
        return None  # Or raise an exception if a user must exist
    return user_data


def find_user_by_username(client: MongoClient, username: str) -> UserModel:
    user_data = connect_to_user_collection(client).find_one({"username": username})
    if user_data is None:
        return None  # Or raise an exception if a user must exist
    return UserModel(**user_data)


def find_all_data(client: MongoClient):
    return list(connect_to_data_collection(client).find())


def find_all_stations(client: MongoClient):
    return list(connect_to_station_collection(client).find())


def find_station_id(client: MongoClient, station_id: int):
    result = list(connect_to_station_collection(client).find({"id": station_id}))
    if len(result) > 1:
        wl.logging.critical('Method: find_station_id(client, id): ' +
                                f'More then one occurrence of the station {id}')
    else:
        if len(result) == 1:
            return result
    return None


def find_all_usernames_for_threshold_station(
        client: MongoClient,
        station_id: int,
        curr_wind_speed: float
    ):
    query = {"station": station_id, "threshold": {"$lte": curr_wind_speed}}
    result = list(connect_to_threshold_collection(client).find(query))
    return [(user['username'], user['threshold']) for user in result]


def find_lowest_threshold_for_station(client: MongoClient, station_id: int):
    pipeline = [
        {"$match": {"station": station_id}},  # Filter by station_id
        {"$group": {"_id": None, "min_threshold": {"$min": "$threshold"}}}
    ]

    result = list(connect_to_threshold_collection(client).aggregate(pipeline))
    return result[0]['min_threshold']  #lowest threshold for specific station id


def clear_user_collection(client: MongoClient):
    x = connect_to_user_collection(client).delete_many({})
    return x.deleted_count


def clear_data_collection(client: MongoClient):
    x = connect_to_data_collection(client).delete_many({})
    return x.deleted_count


def clear_station_collection(client: MongoClient):
    x = connect_to_station_collection(client).delete_many({})
    return x.deleted_count


def clear_threshold_collection(client: MongoClient):
    x = connect_to_threshold_collection(client).delete_many({})
    return x.deleted_count


def clear_windguru_station_collection(client: MongoClient):
    x = connect_to_windguru_station_collection(client).delete_many({})
    return x.deleted_count


def clear_all_collections(client: MongoClient):
    count = clear_user_collection(client)
    count += clear_data_collection(client)
    count += clear_station_collection(client)
    count += clear_threshold_collection(client)
    return count
