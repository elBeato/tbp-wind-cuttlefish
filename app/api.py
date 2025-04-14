# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from pydantic import ValidationError
from app.models import UserModel, ThresholdModel
from app import database as db

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
    """
    API root endpoint
    ---
    tags:
      - Info
    responses:
      200:
        description: Basic API greeting
        content:
          text/html:
            example: "<p>Hello from windseeker app api - more information inside docs<p>"
    """
    return "<p>Hello from windseeker app api - more information inside docs<p>"

@app.route('/', methods=['GET'])
def index():
    """
    Home endpoint
    ---
    tags:
     - Info
    responses:
     200:
       description: Basic homepage message
       content:
         text/html:
           example: "<p>Hello from windseeker app - made with flask and love <3<p>"
    """
    return "<p>Hello from windseeker app - made with flask and love <3<p>"

@app.route('/api/windguru/stations', methods=['GET'])
def get_windguru_stations_all():
    """
    Get all Windguru station IDs and names
    ---
    tags:
     - Windguru
    responses:
     200:
       description: A list of all available Windguru stations
       schema:
         type: object
         properties:
           length:
             type: integer
             example: 23
           additionalInfo:
             type: string
             example: "bla-bla"
           stations:
             type: array
             items:
               type: object
               properties:
                 id:
                   type: string
                   example: "1234"
                 name:
                   type: string
                   example: "Zurichsee"
    """
    try:
        client, db_instance = db.connect_to_db()
        stations = db.find_all_windguru_stations(db_instance)
        # Convert each user document (cursor) to a list and serialize the ObjectId
        station_list = [serialize_user(station) for station in stations]
        filtered_docs = [{'id': doc['id'], 'name': doc['name']} for doc in station_list]
        client.close()
    except Exception as ex:
        return f"<p>Error in Database connection: {ex}<p>"
    return jsonify(
        {
            "length": len(filtered_docs),
            "additionalInfo": "bla-bla",
            "stations": filtered_docs
        }
    )

@app.route('/api/users', methods=['GET'])
def get_users_all():
    """
    Get all users
    ---
    tags:
      - Users
    responses:
      200:
        description: A list of all users
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
                example: "643d2b66c96cfb2fca0a5555"
              name:
                type: string
              email:
                type: string
              mobile:
                type: string
    """
    try:
        client, db_instance = db.connect_to_db()
        users = db.find_all_users(db_instance)
        # Convert each user document (cursor) to a list and serialize the ObjectId
        users_list = [serialize_user(user) for user in users]
        client.close()
    except Exception as ex:
        return f"<p>Error in Database connection: {ex}<p>"
    return jsonify(users_list)

@app.route('/api/users/<username>', methods=['GET'])
def get_users_username_exists(username):
    """
    Check if a username exists
    ---
    tags:
      - Users
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: The username to check
    responses:
      201:
        description: Username availability result
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Username is free to use"
            status:
              type: string
              example: "True"
            user:
              type: object
              nullable: true
    """
    try:
        client, db_instance = db.connect_to_db()
        user = db.find_user_by_username(db_instance, username)
        client.close()
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
    """
    Get all data entries
    ---
    tags:
      - Data
    responses:
      200:
        description: A list of all data entries
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              ...
    """
    try:
        client, db_instance = db.connect_to_db()
        data = db.find_all_data(db_instance)
        # Convert each user document (cursor) to a list and serialize the ObjectId
        data_list = [serialize_data(entry) for entry in data]
        client.close()
    except Exception as ex:
        return f"<p>Error in Database connection: {ex}<p>"
    return jsonify(data_list)

@app.route('/api/thresholds', methods=['POST'])
def post_new_threshold_list():
    """
    Submit a list of threshold configurations
    ---
    tags:
      - Thresholds
    parameters:
      - in: body
        name: thresholds
        required: true
        schema:
          type: array
          items:
            type: object
            properties:
              parameter:
                type: string
                example: "wind_speed"
              min:
                type: number
                example: 5.0
              max:
                type: number
                example: 30.0
    responses:
      201:
        description: Threshold data saved
      400:
        description: Invalid data format
    """
    try:
        data = request.get_json()
        validated_thresholds = [ThresholdModel(**item) for item in data]
        client, db_instance = db.connect_to_db()
        list_thresholds = []
        for threshold in validated_thresholds:
            db.insert_threshold(db_instance, threshold)
            list_thresholds.append(threshold.model_dump())
        client.close()
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
        description: User registration data
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: surfer42
            password:
              type: string
              example: SuperSecret123!
            name:
              type: string
              example: John Doe
            address:
              type: string
              example: 123 Ocean Drive
            email:
              type: string
              format: email
              example: john.doe@example.com
            mobile:
              type: string
              example: "+41 79 123 45 99"
            birthday:
              type: string
              example: "1990-07-15"
            subscriptions:
              type: array
              items:
                type: object
                properties:
                  station_id:
                    type: string
                    example: "windguru-123"
                  alerts_enabled:
                    type: boolean
                    example: true
    responses:
      201:
        description: User created successfully
      400:
        description: Invalid input or JSON format
    """
    try:
        data = request.get_json()
        user = UserModel(**data)  # Validate input using Pydantic

        client, db_instance = db.connect_to_db()
        db.insert_user(db_instance, user)
        inserted_user = db.find_user_by_username(db_instance, user.username)
        # add user to station, create a new station if not exits already
        db.add_user_to_station_by_username(db_instance, inserted_user)
        client.close()
        return jsonify({
            "message": "User data received successfully",
            "user": user.model_dump()
        }), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    user = request.get_json()  # Get JSON data from request
    if not user:
        return jsonify({"error": "No JSON data received"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
