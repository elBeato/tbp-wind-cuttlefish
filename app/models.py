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

class SubscriptionModel(BaseModel):
    """Subscription model class"""
    id: int
    name: str

class UserModel(BaseModel):
    """User model class"""
    _id: ObjectId
    username: str = Field(..., min_length=1, max_length=50)
    password: str
    name: str = Field(..., min_length=1, max_length=100)
    address: str
    email: EmailStr
    mobile: str
    birthday: str
    subscriptions: list[SubscriptionModel]

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

class BasicStationModel(BaseModel):
    """Basic station model"""
    name: str
    id: int = Field(alias='id')  # 'id' in input, 'id' in code

class WindguruStationModel(BasicStationModel):
    """Windguru imported station"""
    online: bool = False

class StationModel(BasicStationModel):
    """Station model with users"""
    subscribers: list


class ThresholdModel(BaseModel):
    """Threshold per station and user"""
    username: str
    station: int
    threshold: float
