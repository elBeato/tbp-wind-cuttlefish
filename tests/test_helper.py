# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
import app.helper as hp
from app import database as db
from unittest.mock import patch, MagicMock
import pytest
from pymongo import MongoClient

@pytest.fixture(scope="function")
def test_db():
    client, db_instance = db.connect_to_db(2000, db_name="windseeker_test")
    db.clear_all_collections(db_instance)
    yield db_instance
    db.clear_all_collections(db_instance)
    client.close()

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db(mock_warning, test_db):
    # Insert test data
    test_db.Stations.insert_one({
        "station_id": "test123",
        "response": {
            "wind_avg": 12,
            "wind_direction": 180
        }
    })

    result = hp.check_response_contains_param(test_db, "test123")
    assert result is True
    mock_warning.assert_not_called()

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db(mock_warning, test_db):
    # Insert test data
    test_db.Stations.insert_one({
        "station_id": "test123",
        "response": {
            "wind_avg": None,
            "wind_direction": 180
        }
    })

    result = hp.check_response_contains_param(test_db, "test123")
    assert result is False
    mock_warning.called()

