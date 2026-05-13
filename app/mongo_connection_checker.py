from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    print("Connected:", client.server_info())
except Exception as e:
    print("Error:", e)