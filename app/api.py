# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from flask_cors import CORS
import database as db

app = Flask(__name__)

# Allow CORS from the frontend (localhost:3000)
CORS(app, origins="*")

def serialize_user(user):
    """Convert MongoDB ObjectId to string and prepare other fields."""
    user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return user

@app.route('/', methods=['GET'])
def index():
    return "<p>Hello world!<p>"

@app.route('/users', methods=['GET'])
def get_users_all():
    client = db.connect_to_db()
    users = db.find_all_users(client)
    # Convert each user document (cursor) to a list and serialize the ObjectId
    users_list = [serialize_user(user) for user in users]
    return jsonify(users_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
