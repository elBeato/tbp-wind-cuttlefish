# -*- coding: utf-8 -*-
from pydantic import BaseModel, EmailStr, Field

class UserModel(BaseModel):
    """User Model class"""
    username: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    address: str
    email: EmailStr
    mobile: str

class DataModel(BaseModel):
    """Data Model class"""
    name: str 
    station: int
    speed: float 
    direction: int
    ts: str
    temp: float