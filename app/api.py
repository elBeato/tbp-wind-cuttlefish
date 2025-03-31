# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from pydantic import ValidationError
from models import UserModel, ThresholdModel
import database as db

app = Flask(__name__)
swagger = Swagger(app) # Initialize Swagger
CORS(app, origins="*") # Allow CORS from the frontend (localhost:3000)

def serialize_user(user):
    """Convert MongoDB ObjectId to string and prepare other fields."""
    user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return user

def serialize_data(data):
    """Convert MongoDB ObjectId to string and prepare other fields."""
    data["_id"] = str(data["_id"])  # Convert ObjectId to string
    return data

@app.route('/api', methods=['GET'])
def index_api():
    return "<p>Hello from windseeker app api - more information inside docs<p>"

@app.route('/', methods=['GET'])
def index():
    return "<p>Hello from windseeker app - made with flusk and love <3<p>"

@app.route('/api/users', methods=['GET'])
def get_users_all():
    try:
        client = db.connect_to_db()
        users = db.find_all_users(client)
        # Convert each user document (cursor) to a list and serialize the ObjectId
        users_list = [serialize_user(user) for user in users]
    except Exception as ex:
        return f"<p>Error in Database connection: {ex}<p>"
    return jsonify(users_list)

@app.route('/api/users/<username>', methods=['GET'])
def get_users_username_exists(username):
    try:
        client = db.connect_to_db()
        user = db.find_user_by_username(client, username)
        if user is None:
            return jsonify({
                "message": "Username is free to use",
                "status": 'True',
                "user": ''
            }), 201
        return jsonify({
            "message": "Username is occupied",
            "status": 'False',
            "user": user.dict()
        }), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/data', methods=['GET'])
def get_data_all():
    try:
        client = db.connect_to_db()
        data = db.find_all_data(client)
        # Convert each user document (cursor) to a list and serialize the ObjectId
        data_list = [serialize_data(entry) for entry in data]
    except Exception as ex:
        return f"<p>Error in Database connection: {ex}<p>"
    return jsonify(data_list)

@app.route('/api/thresholds', methods=['POST'])
def post_new_threshold_list():
    try:
        data = request.get_json()
        validated_thresholds = [ThresholdModel(**item) for item in data]
        client = db.connect_to_db()
        list_thresholds = []
        for threshold in validated_thresholds:
            db.insert_threshold(client, threshold)
            list_thresholds.append(threshold)
        return jsonify({
            "message": "Threshold data received successfully",
            "Thresholds": list_thresholds
            }), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    threshold = request.get_json()  # Get JSON data from request
    if not threshold:
        return jsonify({"error": "No JSON data received"}), 400

@app.route('/api/users', methods=['POST'])
def post_new_users():
    """
    Create a new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: user
        description: User information
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: John Doe
            address:
              type: string
              example: Highway 37
            email:
              type: string
              format: email
              example: john@bluewin.ch
            mobile:
              type: string
              example: "+41 79 123 45 99"
    responses:
      201:
        description: User created successfully
      400:
        description: Invalid JSON format
    """
    try:
        data = request.get_json()
        user = UserModel(**data)  # Validate input using Pydantic

        client = db.connect_to_db()
        db.insert_user(client, user)
        inserted_user = db.find_user_by_username(client, user.username)
        # add user to station, create a new station if not exits already
        db.add_user_to_station_by_username(client, inserted_user)
        return jsonify({
            "message": "User data received successfully",
            "user": user.dict()
        }), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    user = request.get_json()  # Get JSON data from request
    if not user:
        return jsonify({"error": "No JSON data received"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
