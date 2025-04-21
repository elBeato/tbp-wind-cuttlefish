# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
from unittest.mock import patch, MagicMock
import pytest
from requests import ConnectTimeout
import app.helper as hp
from app import database as db
from helper import fetch_data_from_windguru  # replace with actual module

@pytest.fixture(scope="function")
def test_db():
    client, db_instance = db.connect_to_db(2000, db_name="windseeker_test")
    db.clear_all_collections(db_instance)
    yield db_instance
    db.clear_all_collections(db_instance)
    client.close()

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db_1(test_db):
    # Insert test data
    response =  {
            "wind_avg": 3.2,
            "wind_direction": 71.2,
            "temperature": None
        }

    result = hp.check_response_contains_param(response, "test123")
    assert result is True

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db_2(test_db):
    # Insert test data
    response =  {
            "wind_avg": None,
            "wind_direction": 71,
            "temperature": 0
        }

    result = hp.check_response_contains_param(response, "test123")
    assert result is False

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db_3(test_db):
    # Insert test data
    response =  {
            "wind_avg": 3.2,
            "wind_direction": None,
            "temperature": 0
        }

    result = hp.check_response_contains_param(response, "test123")
    assert result is False

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db_4(test_db):
    # Insert test data
    response =  {
            "wind_avg": None,
            "wind_direction": None,
            "temperature": 0
        }

    result = hp.check_response_contains_param(response, "test123")
    assert result is False

# Constants for test
url1 = "https://www.windguru.cz/station/"
url2 = "https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station="
station_id = "12345"

def test_fetch_data_success():
    """Test when requests.get works on the first try."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = 'ok'

    with patch('requests.get', return_value=mock_response) as mock_get:
        response = fetch_data_from_windguru(url1, url2, station_id)

        mock_get.assert_called_once_with(
            f"{url2}{station_id}",
            headers={'Referer': f"{url1}{station_id}"},
            timeout=10
        )
        assert response.status_code == 200
        assert response.text == 'ok'

def test_fetch_data_timeout_retry():
    """Test when the first request times out and the second succeeds."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    # Simulate timeout on first call, success on second
    with patch('requests.get', side_effect=[ConnectTimeout("Timeout!"), mock_response]) as mock_get:
        with patch('time.sleep', return_value=None) as mock_sleep:
            response = fetch_data_from_windguru(url1, url2, station_id)

            assert mock_get.call_count == 2
            mock_sleep.assert_called_once_with(30)

            # Check timeout used in second call
            called_args_list = mock_get.call_args_list
            assert called_args_list[1][1]['timeout'] == 20
            assert response.status_code == 200