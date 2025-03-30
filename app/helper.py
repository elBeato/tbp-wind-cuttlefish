# -*- coding: utf-8 -*-
import json
import database as db

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

def store_users_local_on_host():
    # Connect to MongoDB
    client = db.connect_to_db()
    
    # Fetch all documents
    data = list(db.connect_to_user_collection(client).find())
    
    # Convert ObjectId to string (if needed)
    for doc in data:
        doc["_id"] = str(doc["_id"])
    
    # Save to a JSON file
    with open("backup.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    
    print("✅ Collection exported to backup.json")

store_users_local_on_host()