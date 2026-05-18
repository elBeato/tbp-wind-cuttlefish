# -*- coding: utf-8 -*-
import datetime
from functools import wraps
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
import bcrypt
from pydantic import ValidationError
from app.models import UserModel, ThresholdModel, LoginRequest
from app import database as db
app = Flask(__name__)
swagger = Swagger(app) # Initialize Swagger
CORS(app, origins="*") # Allow CORS from the frontend (localhost:3000)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            request.user_id = payload["user_id"]  # optionally attach to request context
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(*args, **kwargs)

    return decorated

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


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    client, db_instance = db.connect_to_db()
    user = db.find_user_by_id(db_instance, request.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    client.close()
    # Return user data (omit sensitive fields like password)
    return return_user_details(user)


@app.route('/api/auth/me', methods=['PUT'])
@token_required
def update_current_user():
    data = request.get_json()
    client, db_instance = db.connect_to_db()
    user = db.find_user_by_id(db_instance, request.user_id)
    if not user:
        client.close()
        return jsonify({"error": "User not found"}), 404  
    
    # Update user fields (except password and username)
    update_fields = ["name", "address", "email", "mobile", "birthday"]
    for field in update_fields:
        if field in data:
            user[field] = data[field]
    db.update_user_by_id(db_instance, user["username"], user)
    updated_user = db.find_user_by_id(db_instance, request.user_id)   
    client.close()
    # Return user data (omit sensitive fields like password)
    return return_user_details(updated_user)


@app.route('/api/auth/me/password', methods=['PUT'])
@token_required
def change_user_password():
    data = request.get_json()
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    if not current_password or not new_password:
        return jsonify({"error": "Current password and new password are required"}), 400
    client, db_instance = db.connect_to_db()
    user = db.find_user_by_id(db_instance, request.user_id)
    if not user:
        client.close()
        return jsonify({"error": "User not found"}), 404
    if not user or not bcrypt.checkpw(current_password.encode(), user['password'].encode()):
        client.close()
        return jsonify({"error": "Current password is incorrect"}), 401

    db.update_user_password_by_id(db_instance, request.user_id, new_password)
    updated_user = db.find_user_by_id(db_instance, request.user_id)
    client.close()
    return return_user_details(updated_user)


@app.route('/api/auth/me', methods=['DELETE'])
@token_required
def delete_current_user():
    client, db_instance = db.connect_to_db()
    user = db.find_user_by_id(db_instance, request.user_id)
    if not user:
        client.close()
        return jsonify({"error": "User not found"}), 404
    # Archive the user data before deletion and then delete the user
    db.archive_user(db_instance, request.user_id)
    client.close()

    return jsonify({"message": "User deleted successfully"}), 200


@app.route('/api/auth/me/subscription', methods=['POST'])
@token_required
def add_subscription():
    data = request.get_json()
    station_id = data.get("station_id")
    threshold = data.get("threshold", 0.0)

    if not station_id:
        return jsonify({"error": "No station ID provided"}), 400

    client, db_instance = db.connect_to_db()
    user = db.find_user_by_id(db_instance, request.user_id)

    if not user:
        client.close()
        return jsonify({"error": "User not found"}), 404

    
    if db.find_station_id(db_instance, station_id) is None:
        station = db_instance.WindguruStations.find_one({"id": station_id})
        if not station:
            client.close()
            return jsonify({"error": "Station not found"}), 404
        
        db.add_station(db_instance, station, user["username"])
    else:
        db.update_station_subscribers(db_instance, station_id, user["username"])

    db.add_subscription_to_user(db_instance, user["username"], station_id, threshold)
    updated_user = db.find_user_by_id(db_instance, request.user_id)
    client.close()

    return return_user_details(updated_user), 200


@app.route('/api/auth/me/subscription', methods=['DELETE'])
@token_required
def delete_subscription():
    data = request.get_json()
    station_id = data.get("station_id")

    if not station_id:
        return jsonify({"error": "No station ID provided"}), 400
    print(f"Received request to remove subscription for station: {station_id}")
    client, db_instance = db.connect_to_db()
    user = db.find_user_by_id(db_instance, request.user_id)

    if not user:
        client.close()
        return jsonify({"error": "User not found"}), 404
    print(f"Removing subscription for user: {user['username']} from station: {station_id}")
    db.remove_subscription_from_user(db_instance, user["username"], station_id, user)
    updated_user = db.find_user_by_id(db_instance, request.user_id)
    client.close()

    return return_user_details(updated_user), 200


@app.route('/api/auth/me/subscription', methods=['GET'])
def unsubscribe_via_link():
    token = request.args.get('unsubscribe_token')

    if not token:
        return jsonify({"error": "Missing unsubscribe token"}), 400

    client, db_instance = db.connect_to_db()
    token_doc = db.get_valid_unsubscribe_token(db_instance, token)

    if not token_doc:
        client.close()
        return jsonify({"error": "Invalid or expired token"}), 400

    user_id = token_doc['user_id']
    station_id = token_doc['station_id']

    user = db.find_user_by_id(db_instance, user_id)
    if not user:
        client.close()
        return jsonify({"error": "User not found"}), 404

    db.remove_subscription_from_user(db_instance, user["username"], station_id, user)

    db.mark_token_used(db_instance, token)
    client.close()

    return jsonify({"message": "Successfully unsubscribed from station alerts"}), 200


@app.route('/api/auth/me/notification', methods=['PUT', 'OPTIONS'])
@token_required
def update_notification_channel():
    if request.method == 'OPTIONS':
        return '', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT',
            'Access-Control-Allow-Headers': 'Authorization, Content-Type'
        }

    data = request.get_json()
    new_channel = data.get("notification_channel")

    if not new_channel:
        return jsonify({"error": "No notification channel provided"}), 400

    client, db_instance = db.connect_to_db()
    user = db.find_user_by_id(db_instance, request.user_id)

    if not user:
        client.close()
        return jsonify({"error": "User not found"}), 404

    db.update_user_notification_channel(db_instance, user["username"], new_channel)
    updated_user = db.find_user_by_id(db_instance, request.user_id)
    client.close()

    return return_user_details(updated_user), 200


@app.route('/api/auth/me/thresholds', methods=['GET'])
@token_required
def get_thresholds_by_username():
    client, db_instance = db.connect_to_db()
    user = db.find_user_by_id(db_instance, request.user_id)
    if not user:
        client.close()
        return jsonify({"error": "User not found"}), 404
    thresholds = db.find_all_thresholds_by_username(db_instance, user["username"])
    client.close()
    return jsonify([
      {
          "username": el["username"],
          "station": el["station"],
          "threshold": el["threshold"]
      }
      for el in thresholds
    ])  


@app.route('/api/auth/me/threshold', methods=['PUT'])
@token_required
def update_threshold():
    data = request.get_json()
    station_id = data.get("station_id")
    new_threshold = data.get("new_threshold")
     
    client, db_instance = db.connect_to_db()
    user = db.find_user_by_id(db_instance, request.user_id)

    if not user:
        client.close()
        return jsonify({"error": "User not found"}), 404

    db.update_user_threshold(db_instance, user["username"], station_id, new_threshold)
    updated_thresholds = db.find_all_thresholds_by_username(db_instance, user["username"])
    client.close()

    return jsonify([
      {
          "username": el["username"],
          "station": el["station"],
          "threshold": el["threshold"]
      }
      for el in updated_thresholds
    ]), 200


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
        client.close()
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
        client.close()
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
        client.close()
        return jsonify({"error": str(e)}), 400


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
            notification_channel:
              type: string
              example: "email"
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
        client.close()
        return jsonify({"error": str(e)}), 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = LoginRequest(**request.json)
        client, db_instance = db.connect_to_db()
        user = db.find_user_by_credentials(db_instance, data)
        client.close()
        if not user or not bcrypt.checkpw(data.password.encode(), user['password'].encode()):
            client.close()
            return jsonify({"error": "Invalid credentials"}), 401

        payload = {
            "user_id": str(user["_id"]),
            "exp": datetime.datetime.now() + datetime.timedelta(days=1)
        }
        # Install PyJWT with 'pip3 install PyJWT' if you haven't already. Not: JWT library.")
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        return jsonify({"token": token})

    except Exception as e:
        client.close()
        print(f"Login error: {e}")
        return jsonify({"error": str(e)}), 400


# Helper function to return user details without sensitive information
def return_user_details(user):
    client, db_instance = db.connect_to_db()
    
    subscriptions_with_names = []
    for sub in user.get("subscriptions", []):
        station_id = sub.get("id") or sub.get("station")
        station = db_instance.WindguruStations.find_one({"id": station_id})
        station_name = station["name"] if station else "Unknown"
        subscriptions_with_names.append({
            "id": station_id,
            "name": station_name
        })
    
    client.close()
    
    return jsonify({
        "notification_channel": user["notification_channel"],
        "username": user["username"],
        "email": user["email"],
        "name": user["name"],
        "address": user["address"],
        "mobile": user["mobile"],
        "birthday": user["birthday"],
        "subscriptions": subscriptions_with_names
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
