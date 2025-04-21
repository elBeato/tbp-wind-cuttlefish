import datetime
import re
from bson import ObjectId
import pytest
from app.models import (
    UserModel, DataModel,
    WindguruStationModel,
    ThresholdModel, hash_password
)


def test_hash_password_generates_hash():
    raw_password = "mysupersecurepassword"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert re.match(r"^\$2[aby]?\$[0-9]{2}\$.*", hashed)


def test_user_model_creation_and_password_hashing():
    user_data = {
        "_id": ObjectId(),
        "username": "johndoe",
        "password": "plaintext",
        "name": "John Doe",
        "address": "123 Street",
        "email": "john@example.com",
        "mobile": "1234567890",
        "birthday": "1990-01-01",
        "subscriptions": [{"id": 1, "name": "Newsletter"}]
    }

    user = UserModel(**user_data)
    assert user.username == "johndoe"
    user.hash_user_password()
    assert user.password != "plaintext"
    assert user.password.startswith("$2")  # bcrypt prefix


def test_data_model_validation():
    data = DataModel(
        name="Station Alpha",
        station=101,
        speed=12.5,
        direction=270,
        ts="2024-04-01T12:00:00Z",
        temp=18.0,
        createdAt=datetime.datetime.now()
    )
    assert data.station == 101
    assert isinstance(data.speed, float)


def test_windguru_station_defaults():
    station = WindguruStationModel(id=123, name="Test Station")
    assert station.id == 123
    assert station.online is False


def test_threshold_model_validation():
    threshold = ThresholdModel(username="johndoe", station=42, threshold=7.5)
    assert threshold.station == 42
    assert isinstance(threshold.threshold, float)


def test_invalid_email_in_user_model():
    with pytest.raises(ValueError):
        UserModel(
            _id=ObjectId(),
            username="testuser",
            password="test123",
            name="Test User",
            address="Somewhere",
            email="invalid-email",  # <--- invalid email
            mobile="0000000000",
            birthday="2000-01-01",
            subscriptions=[]
        )
