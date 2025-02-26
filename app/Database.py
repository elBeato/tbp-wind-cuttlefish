# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 10:45:13 2025

@author: fub
"""
import pymongo

def connect_to_user_collection(client, dbName, collName):
    db = client[dbName]
    return db[collName]


def connect_to_db(dbName, collName):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
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
    
    
def find_all(userCollection):
    return userCollection.find()

if __name__ == '__main__':
    dbName = "Windseeker"
    collName = "Users"
    
    mongoClient = connect_to_db(dbName, collName)
    userCollection = connect_to_user_collection(mongoClient, dbName, collName)
    
    insert_user(userCollection)
    for u in find_all(userCollection):
        print(u)