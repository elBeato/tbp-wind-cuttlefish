# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 10:45:13 2025

@author: fub
"""
import pymongo
import configuration as config

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


def connect_to_db():
    myclient = pymongo.MongoClient("mongodb://root:supersecurepassword@localhost:28017/")
    dblist = myclient.list_database_names()
    db_name = get_database_name()
    if db_name in dblist:
        print("Database exists.")
    return myclient

def insert_user(client, user):
    connect_to_user_collection(client).insert_one(user)

def insert_data(client, data):
    connect_to_data_collection(client).insert_one(data)

def find_all_users(client):
    return connect_to_user_collection(client).find()

def find_all_data(client):
    return connect_to_data_collection(client).find()

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
