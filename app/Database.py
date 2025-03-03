# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 10:45:13 2025

@author: fub
"""
import pymongo

def connect_to_collection(client, db_name, coll_name):
    """
    

    Parameters
    ----------
    client : TYPE
        DESCRIPTION.
    db_name : TYPE
        DESCRIPTION.
    coll_name : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    db = client[db_name]
    return db[coll_name]


def connect_to_db(db_name, coll_name):
    """
    

    Parameters
    ----------
    db_name : TYPE
        DESCRIPTION.
    coll_name : TYPE
        DESCRIPTION.

    Returns
    -------
    myclient : TYPE
        DESCRIPTION.

    """
    myclient = pymongo.MongoClient("mongodb://root:supersecurepassword@localhost:28017/")
    dblist = myclient.list_database_names()
    if db_name in dblist:
        print("Database exists.")

    collist = myclient["Windseeker"].list_collection_names()
    if coll_name in collist:
        print("Collection exists.")

    return myclient


def insert_user(userCollection):
    """
    

    Parameters
    ----------
    userCollection : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    myUser = { "name": "John",
              "address": "Highway 37", 
              "email": "john@bluewin.ch", 
              "mobile": "+41 79 123 45 99" 
              }
    userCollection.insert_one(myUser)


def insert_data(userCollection, data):
    userCollection.insert_one(data)


def find_all(userCollection):
    return userCollection.find()
