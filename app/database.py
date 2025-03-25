# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 10:45:13 2025

@author: fub
"""
import pymongo
import configuration as config

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

def connect_to_user_collection(client):
    database = client[get_database_name()]
    return database[get_user_collection()]

def connect_to_data_collection(client):
    database = client[get_database_name()]
    return database[get_data_collection()]

def insert_user(client, user):
    connect_to_user_collection(client).insert_one(user)

def insert_data(client, data):
    connect_to_data_collection(client).insert_one(data)

def find_all_users(client):
    return list(connect_to_user_collection(client).find())

def find_all_data(client):
    return list(connect_to_data_collection(client).find())

def clear_user_collection(client):
    x = connect_to_user_collection(client).delete_many({})
    return x.deleted_count

def clear_data_collection(client):
    x = connect_to_data_collection(client).delete_many({})
    return x.deleted_count

def clear_all_collections(client):
    count = clear_user_collection(client)
    count += clear_data_collection(client)
    return count
