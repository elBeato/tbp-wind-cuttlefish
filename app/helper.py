# -*- coding: utf-8 -*-
import json
import database as db
import windlogger as wl

# Using a closure function with enclosed state
def counter():
    count = 0  # Initial counter value

    def increment(reset=False):
        nonlocal count  # Use nonlocal to modify the outer variable
        if reset:
            count = 0
        else:
            count += 1
        return count

    return increment

def store_collections_local_on_host() -> bool:
    # Connect to MongoDB
    client = db.connect_to_db()

    # Fetch all documents
    user = list(db.connect_to_user_collection(client).find())
    station = list(db.connect_to_station_collection(client).find())
    threshold = list(db.connect_to_threshold_collection(client).find())

    # Convert ObjectId to string (if needed)
    for doc in user:
        doc["_id"] = str(doc["_id"])

    for doc in station:
        doc["_id"] = str(doc["_id"])

    for doc in threshold:
        doc["_id"] = str(doc["_id"])

    # Save to a JSON file
    with open("user_backup.json", "w", encoding="utf-8") as file:
        json.dump(user, file, indent=4)
    with open("station_backup.json", "w", encoding="utf-8") as file:
        json.dump(station, file, indent=4)
    with open("threshold_backup.json", "w", encoding="utf-8") as file:
        json.dump(threshold, file, indent=4)

    wl.logger.info("Collection exported to user_backup.json")
    wl.logger.info("Collection exported to station_backup.json")
    wl.logger.info("Collection exported to threshold_backup.json")
    return True
