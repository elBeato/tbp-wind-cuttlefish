# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 10:45:13 2025

@author: fub
"""
import pymongo

def connect_to_collection(client, dbName, collName):
    db = client[dbName]
    return db[collName]


def connect_to_db(dbName, collName):
    myclient = pymongo.MongoClient("mongodb://root:supersecurepassword@localhost:28017/")
    dblist = myclient.list_database_names()
    if dbName in dblist:
        print("Database exists.")
        
    collist = myclient["Windseeker"].list_collection_names()
    if collName in collist:
        print("Collection exists.")
        
    return myclient


def insert_user(userCollection):
    myUser = { "name": "John", "address": "Highway 37", "email": "john@bluewin.ch", "mobile": "+41 79 123 45 99" }
    userCollection.insert_one(myUser)


def insert_data(userCollection, data):
    userCollection.insert_one(data)
    
    
def find_all(userCollection):
    return userCollection.find()

if __name__ == '__main__':
    dbName = "Windseeker"
    collName = "Users"
    collData = "WindData"
    
    mongoClient = connect_to_db(dbName, collName)
    userCollection = connect_to_collection(mongoClient, dbName, collName)
    dataCollection = connect_to_collection(mongoClient, dbName, collData)
    
    insert_user(userCollection)
    insert_data(dataCollection, {
        "station": 1235, 
        "speed": 22.8, 
        "direction": 102, 
        "ts": '2025-03-03 10:02:48 CET', 
        "temp": 3.5
    })
    for u in find_all(userCollection):
        print(u)