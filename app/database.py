# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 10:45:13 2025

@author: fub
"""
from pymongo import MongoClient, errors, ASCENDING
from bson.objectid import ObjectId
from rpds import List
import uuid
import datetime
from app import configuration as config
from app import windlogger as wl
from app.models import UserModel, DataModel, StationModel, ThresholdModel, WindguruStationModel, hash_password

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


def add_station(database: MongoClient, station: str, identification: str):
    new_station = StationModel(name=station["name"], id=station["id"], subscribers=[identification])
    insert_station(database, new_station)


def archive_user(database: MongoClient, user_id):
    user_data = find_user_by_id(database, user_id)
    if user_data is None:
        return False  # User not found
    database.RemovedUsers.insert_one(user_data)  # Archive the user data
    database.Users.delete_one({"_id": ObjectId(user_id)})  # Remove from active users
    return True


def connect_to_db(timeout_ms=5000, db_name='Windseeker'):
    """Connects to MongoDB and checks if the connection is healthy."""
    try:
        host = config.get_config_value("MONGO_HOST")
        port = config.get_config_value("MONGO_PORT")
        user = config.get_config_value("MONGO_USERNAME")
        password = config.get_config_value("MONGO_PASSWORD")
        print(f"Connecting to MongoDB at {host}:{port} with user '{user}'")
        if user is None or user == "" or password is None or password == "":
            print("Using not authentication for MongoDB connection.")
            client = MongoClient(f"mongodb://{host}:{port}/")
        else:
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


def create_data_collection(database):
    collection = database.Data
    collection.create_index(
        [("createdAt", ASCENDING)],
        expireAfterSeconds=1209600 # 14 days in seconds
    )


def create_indexes_all_collections(database):
    create_user_collection(database)
    create_station_collection(database)
    create_threshold_collection(database)
    create_windguru_station_collection(database)
    create_data_collection(database)
    create_removed_user_collection(database)
    create_unsubscribe_token_collection(database)

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

def create_removed_user_collection(database: MongoClient):
    collection = database.RemovedUsers
    # Ensure uniqueness of the 'id' field
    collection.create_index("id", unique=True)


def remove_subscription_from_user(database: MongoClient, username: str, station_id: int, user: dict = None):
    try:
        database.Thresholds.delete_one({"username": username, "station": station_id})
        database.Users.update_one(
            {"username": username},
            {"$pull": {"subscriptions": {"id": station_id}}}   
        )
        pull_candidates = [username]
        if user:
            pull_candidates.append(user["_id"])
        database.Stations.update_one(
            {"id": station_id},
            {"$pull": {"subscribers": {"$in": pull_candidates}}}
        )
    except Exception as ex:
        wl.logging.error(f'Method: remove_subscription_from_user(client, username, station_id): {ex}')    

def add_subscription_to_user(database: MongoClient, username: str, station_id: int, threshold: float = 0.0):
    try:
        insert_threshold(database, ThresholdModel(username=username, station=station_id, threshold=threshold))
        database.Users.update_one(
            {"username": username},
            {"$push": {"subscriptions": {"id": station_id}}}   
        )
    except Exception as ex:
        wl.logging.error(f'Method: add_subscription_to_user(client, username, station_id, threshold): {ex}')    


def update_user_password_by_id(database: MongoClient, user_id: str, new_password: str):
    try:
        hashed_password = hash_password(new_password)
        database.Users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed_password}}
        )
        return None
    except Exception as ex:
        wl.logging.error(f'Method: change_password(client, username, new_password): {ex}')
        return None

def insert_user(database: MongoClient, user: UserModel):
    try:
        user.hash_user_password()
        result = database.Users.insert_one(user.model_dump(by_alias=True, exclude_none=True))
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
    try:
        docs = [station.model_dump(by_alias=True) for station in windguru_stations]
    except Exception as ex:
        wl.logging.error(f'Method: insert_windguru_station(client, windguru_stations): {ex}')
        return 0

    try:
        result = database.WindguruStations.insert_many(docs)
        return len(result.inserted_ids)
    except Exception as ex:
        wl.logging.error(f'Method: insert_windguru_station(client, windguru_stations): {ex}')
        return 0

def add_user_to_station_by_id(database: MongoClient, user):
    identification = user['_id']
    add_user_to_station(database, UserModel(**user), identification)


def add_user_to_station_by_username(database: MongoClient, user: UserModel):
    identification = user.username
    add_user_to_station(database, user, identification)


def find_all_users(database: MongoClient):
    return list(database.Users.find())

def find_user_by_credentials(database: MongoClient, data) -> UserModel:
    # Search by either username or email
    user = database.Users.find_one({
        "$or": [
            {"username": data.identifier},
            {"email": data.identifier}
        ]
    })
    return user

def find_all_windguru_stations(database: MongoClient):
    return list(database.WindguruStations.find())

def find_user_by_id(database: MongoClient, user_id):
    user_data = database.Users.find_one({"_id": ObjectId(user_id)})
    if user_data is None:
        return None  # Or raise an exception if a user must exist
    print(f"Found user: {user_data} with ID: {user_id}")
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


def find_all_thresholds_by_username(database: MongoClient, username: str):
    query = {"username": username}
    return list(database.Thresholds.find(query))


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


def update_user_by_id(database: MongoClient, username, updated_user):
    print(f"Updating user with ID '{username}' to '{updated_user}'")
    if hasattr(updated_user, 'model_dump'):
        update_data = updated_user.model_dump()
    else:
        update_data = updated_user
    result = database.Users.update_one(
        {"username": username},
        {"$set": update_data}
    )
    return result.modified_count > 0


def update_user_notification_channel(database: MongoClient, username: str, new_channel: str):
    try: 
        print(f"Updating notification channel for user '{username}' to '{new_channel}'")
        if new_channel not in ['email', 'mobile', 'email_and_mobile', 'without_notification']:
            raise ValueError("Invalid notification channel. Must be 'email','mobile' or 'without_notification'.")
        print(f"Updating notification channel for user '{username}' to '{new_channel}'")
    except Exception as ex:
        wl.logging.error(f'Method: update_user_notification_channel(client, username, new_channel): {ex}')
        return False

    try:
        result = database.Users.update_one(
            {"username": username},
            {"$set": {"notification_channel": new_channel}}     
        )
        return result.modified_count > 0
    except Exception as ex:
        wl.logging.error(f'Method: update_user_notification_channel(client, username, new_channel): {ex}')
        return False 


def update_user_threshold(database: MongoClient, username: str, station_id: int, new_threshold: float):
    try:
        print(f"Updating threshold for user '{username}' and station '{station_id}' to '{new_threshold}'")
        if new_threshold < 0:
            raise ValueError("Threshold must be a non-negative value.")
    except Exception as ex:
        wl.logging.error(f'Method: update_user_threshold(client, username, station_id, new_threshold): {ex}')
        return False

    try:
        result = database.Thresholds.update_one(
            {"username": username, "station": station_id},
            {"$set": {"threshold": new_threshold}}
        )
        return result.modified_count > 0
    except Exception as ex:
        wl.logging.error(f'Method: update_user_threshold(client, username, station_id, new_threshold): {ex}')
        return False

def update_station_subscribers(database: MongoClient, station_id, identification: str):
    try:
        database.Stations.update_one(
                {"id": station_id},
                {"$push": {"subscribers": identification}}
            )
    except Exception as ex:
        wl.logging.error(f'Method: update_station_subscribers(client, station, identification): {ex}')
        return False


def create_unsubscribe_token_collection(database: MongoClient):
    collection = database.UnsubscribeTokens
    collection.create_index("token", unique=True)
    collection.create_index("created_at", expireAfterSeconds=86400)


def create_unsubscribe_token(database: MongoClient, user_id: str, station_id: int) -> str:
    try:
        token = str(uuid.uuid4())
        token_doc = {
            "token": token,
            "user_id": user_id,
            "station_id": station_id,
            "created_at": datetime.datetime.now(),
            "used": False
        }
        database.UnsubscribeTokens.insert_one(token_doc)
        return token
    except Exception as ex:
        wl.logging.error(f'Method: create_unsubscribe_token(client, user_id, station_id): {ex}')
        return None


def get_valid_unsubscribe_token(database: MongoClient, token: str) -> dict:
    try:
        token_doc = database.UnsubscribeTokens.find_one({
            "token": token,
            "used": False
        })
        if token_doc:
            expiry_time = token_doc["created_at"] + datetime.timedelta(hours=24)
            if datetime.datetime.now() > expiry_time:
                return None
        return token_doc
    except Exception as ex:
        wl.logging.error(f'Method: get_valid_unsubscribe_token(client, token): {ex}')
        return None


def mark_token_used(database: MongoClient, token: str):
    try:
        database.UnsubscribeTokens.update_one(
            {"token": token},
            {"$set": {"used": True}}
        )
    except Exception as ex:
        wl.logging.error(f'Method: mark_token_used(client, token): {ex}')
