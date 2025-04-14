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

def add_user_to_station(database: MongoClient, user: UserModel, identification):
    for station in user.subscriptions:
        if find_station_id(database, station.id) is None:
            my_list = [identification]
            my_station = {
                "name": station.name,
                "id": station.id,
                "subscribers": my_list
            }
            station = StationModel(**my_station)
            insert_station(database, station)
        else:
            database.Stations.update_one(
                {"id": station.id},
                {"$push": {"subscribers": identification}}
            )


def connect_to_db(timeout_ms=5000, db_name='Windseeker'):
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
        return client, client[db_name]  # Return the client if connection is successful

    except errors.ConnectionFailure as ex:
        string = 'MongoDB connection failed: %s', str(ex)
        wl.logger.error(string)
        return None  # Return None if connection fails

def create_indexes_all_collections(database):
    create_user_collection(database)
    create_station_collection(database)
    create_threshold_collection(database)
    create_windguru_station_collection(database)

def create_windguru_station_collection(database: MongoClient):
    collection = database.WindguruStations
    # Ensure uniqueness of the 'id' field
    collection.create_index("id", unique=True)

def create_user_collection(database: MongoClient):
    collection = database.Users
    # Ensure uniqueness of the 'id' field
    collection.create_index("username", unique=True)

def create_station_collection(database: MongoClient):
    collection = database.Stations
    # Ensure uniqueness of the 'id' field
    collection.create_index("id", unique=True)

def create_threshold_collection(database: MongoClient):
    collection = database.Thresholds
    # Create the compound unique index on 'username' and 'station'
    collection.create_index(["username", "station"], unique=True)


def insert_user(database: MongoClient, user: UserModel):
    try:
        user.hash_user_password()
        result = database.Users.insert_one(user.model_dump())
        return str(result.inserted_id)
    except Exception as ex:
        wl.logging.error(f'Method: insert_user(client, user): {ex}')
    return None


def insert_data(database: MongoClient, data: DataModel):
    database.Data.insert_one(data.model_dump())


def insert_station(database: MongoClient, station: StationModel):
    database.Stations.insert_one(station.model_dump())


def insert_threshold(database: MongoClient, threshold: ThresholdModel):
    database.Thresholds.insert_one(threshold.model_dump())

def insert_windguru_station(database: MongoClient, windguru_stations: list[WindguruStationModel]):
    docs = [station.model_dump(by_alias=True) for station in windguru_stations]
    result = database.WindguruStations.insert_many(docs)
    return len(result.inserted_ids)

def add_user_to_station_by_id(database: MongoClient, user):
    identification = user['_id']
    add_user_to_station(database, UserModel(**user), identification)


def add_user_to_station_by_username(database: MongoClient, user: UserModel):
    identification = user.username
    add_user_to_station(database, user, identification)


def find_all_users(database: MongoClient):
    return list(database.Users.find())


def find_all_windguru_stations(database: MongoClient):
    return list(database.WindguruStations.find())

def find_user_by_id(database: MongoClient, user_id):
    user_data = database.Users.find_one({"_id": ObjectId(user_id)})
    if user_data is None:
        return None  # Or raise an exception if a user must exist
    return user_data


def find_user_by_username(database: MongoClient, username: str) -> UserModel:
    user_data = database.Users.find_one({"username": username})
    if user_data is None:
        return None  # Or raise an exception if a user must exist
    return UserModel(**user_data)


def find_all_data(database: MongoClient):
    return list(database.Data.find())


def find_all_stations(database: MongoClient):
    return list(database.Stations.find())


def find_station_id(database: MongoClient, station_id: int):
    result = list(database.Stations.find({"id": station_id}))
    if len(result) > 1:
        wl.logging.critical('Method: find_station_id(client, id): ' +
                                f'More then one occurrence of the station {id}')
    else:
        if len(result) == 1:
            return result
    return None


def find_all_usernames_for_threshold_station(
        database: MongoClient,
        station_id: int,
        curr_wind_speed: float
    ):
    query = {"station": station_id, "threshold": {"$lte": curr_wind_speed}}
    result = list(database.Thresholds.find(query))
    return [(user['username'], user['threshold']) for user in result]


def find_lowest_threshold_for_station(database: MongoClient, station_id: int):
    pipeline = [
        {"$match": {"station": station_id}},  # Filter by station_id
        {"$group": {"_id": None, "min_threshold": {"$min": "$threshold"}}}
    ]

    result = list(database.Thresholds.aggregate(pipeline))
    return result[0]['min_threshold']  #lowest threshold for specific station id


def clear_user_collection(database: MongoClient):
    x = database.Users.delete_many({})
    return x.deleted_count


def clear_data_collection(database: MongoClient):
    x = database.Data.delete_many({})
    return x.deleted_count


def clear_station_collection(database: MongoClient):
    x = database.Stations.delete_many({})
    return x.deleted_count


def clear_threshold_collection(database: MongoClient):
    x = database.Thresholds.delete_many({})
    return x.deleted_count


def clear_windguru_station_collection(database: MongoClient):
    x = database.WindguruStations.delete_many({})
    return x.deleted_count

def clear_all_collections(db):
    db.Users.delete_many({})
    db.Data.delete_many({})
    db.Stations.delete_many({})
    db.Thresholds.delete_many({})
    return 0
