# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
from unittest.mock import patch, MagicMock
from requests import ConnectTimeout
import app.helper as hp

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db_1():
    # Insert test data
    response =  {
            "wind_avg": 3.2,
            "wind_direction": 71.2,
            "temperature": None
        }

    result = hp.check_response_contains_param(response, "test123")
    assert result is True

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db_2():
    # Insert test data
    response =  {
            "wind_avg": None,
            "wind_direction": 71,
            "temperature": 0
        }

    result = hp.check_response_contains_param(response, "test123")
    assert result is False

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db_3():
    # Insert test data
    response =  {
            "wind_avg": 3.2,
            "wind_direction": None,
            "temperature": 0
        }

    result = hp.check_response_contains_param(response, "test123")
    assert result is False

@patch("app.windlogger.logger.warning")
def test_response_data_valid_from_db_4():
    # Insert test data
    response =  {
            "wind_avg": None,
            "wind_direction": None,
            "temperature": 0
        }

    result = hp.check_response_contains_param(response, "test123")
    assert result is False

# Constants for test
URL_1 = "https://www.windguru.cz/station/"
URL_2 = "https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station="
STATION_ID = "12345"

def test_fetch_data_success():
    """Test when requests.get works on the first try."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = 'ok'

    with patch('requests.get', return_value=mock_response) as mock_get:
        response = hp.fetch_data_from_windguru(URL_1, URL_2, STATION_ID)

        mock_get.assert_called_once_with(
            f"{URL_2}{STATION_ID}",
            headers={'Referer': f"{URL_1}{STATION_ID}"},
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
            response = hp.fetch_data_from_windguru(URL_1, URL_2, STATION_ID)

            assert mock_get.call_count == 2
            mock_sleep.assert_called_once_with(30)

            # Check timeout used in second call
            called_args_list = mock_get.call_args_list
            assert called_args_list[1][1]['timeout'] == 20
            assert response.status_code == 200
