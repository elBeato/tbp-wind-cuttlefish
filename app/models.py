# -*- coding: utf-8 -*-
from pydantic import BaseModel, EmailStr, Field
from bson.objectid import ObjectId
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

example = {
    "address":"Hellgasse 500",
    "mobile":"012",
    "birthday":"1986-11-20",
    "username":"elBeato",
    "email":"beatus.furrer@gmail.com",
    "password":"123",
    "subscriptions":[1234, 5678]
    }

class UserModel(BaseModel):
    """User Model class"""
    _id: ObjectId
    username: str = Field(..., min_length=1, max_length=50)
    password: str
    name: str = Field(..., min_length=1, max_length=100)
    address: str
    email: EmailStr
    mobile: str
    birthday: str
    subscriptions: list

    def hash_user_password(self):
        """Hash the password before storing the user."""
        self.password = hash_password(self.password)

class DataModel(BaseModel):
    """Data Model class"""
    name: str
    station: int
    speed: float
    direction: int
    ts: str
    temp: float

class StationModel(BaseModel):
    """Station model with users"""
    name: str
    number: int
    subscribers: list

class ThresholdModel(BaseModel):
    """Threshold per station and user"""
    username: str
    station: int
    threshold: float
