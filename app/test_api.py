# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
import startup
import helper as hp

def test_call_windguru_api():
    station_id = 2736
    count_func = hp.counter()
    req = startup.windguru_api_call(
        'https://www.windguru.cz/station/', 
        'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=', 
        station_id,
        count_func,
        30,
        90
    )
    expected = "https://www.windguru.cz/int/iapi.php?" \
        "q=station_data_current&id_station=" + str(station_id)

    assert req.url == expected
    assert req.status_code == 200
    assert req.encoding == 'utf-8'
    assert req.content is not None
    assert req.content != {}

def test_call_windguru_api_types():
    station_id = 5931  # Ho'okipa Maui
    count_func = hp.counter()
    req = startup.windguru_api_call(
        'https://www.windguru.cz/station/', 
        'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=', 
        station_id,
        count_func,
        30,
        90
    )
    expected = "https://www.windguru.cz/int/iapi.php?" \
        "q=station_data_current&id_station=" + str(station_id)

    response = req.json()
    wind_avg = response['wind_avg']
    wind_max = response['wind_max']
    wind_min = response['wind_min']
    wind_direction = response['wind_direction']
    temperature = response['temperature']
    datetime = response['datetime']
    unixtime = response['unixtime']

    assert req.url == expected
    assert isinstance(wind_avg, float)
    assert isinstance(wind_max, float)
    assert isinstance(wind_min, float)
    assert isinstance(wind_direction, int)
    assert isinstance(temperature, float)
    assert isinstance(datetime, str)
    assert isinstance(unixtime, int)

def test_call_windguru_api_values():
    station_id = 5931  # Ho'okipa Maui
    count_func = hp.counter()
    req = startup.windguru_api_call(
        'https://www.windguru.cz/station/', 
        'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=', 
        station_id,
        count_func,
        30,
        90
    )
    expected = "https://www.windguru.cz/int/iapi.php?" \
        "q=station_data_current&id_station=" + str(station_id)

    response = req.json()
    wind_avg = response['wind_avg']
    wind_max = response['wind_max']
    wind_min = response['wind_min']
    wind_direction = response['wind_direction']
    temperature = response['temperature']
    datetime = response['datetime']
    unixtime = response['unixtime']

    assert req.url == expected
    assert response is not None
    assert wind_avg >= 0.0
    assert wind_max >= 0.0
    assert wind_min >= 0.0
    assert wind_direction >= 0
    assert temperature >= -80.0
    assert unixtime >= 0

    assert isinstance(wind_avg, float)
    assert isinstance(wind_max, float)
    assert isinstance(wind_min, float)
    assert isinstance(wind_direction, int)
    assert isinstance(temperature, float)
    assert isinstance(datetime, str)
    assert isinstance(unixtime, int)

def test_call_windguru_api_print_values():
    station_id = 5931  # Ho'okipa Maui
    count_func = hp.counter()
    req = startup.windguru_api_call(
        'https://www.windguru.cz/station/', 
        'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=', 
        station_id,
        count_func,
        30,
        90
    )
    expected = "https://www.windguru.cz/int/iapi.php?" \
        "q=station_data_current&id_station=" + str(station_id)

    response = req.json()
    wind_avg = response['wind_avg']
    wind_max = response['wind_max']
    wind_min = response['wind_min']
    wind_direction = response['wind_direction']
    temperature = response['temperature']
    datetime = response['datetime']
    unixtime = response['unixtime']

    assert req.url == expected

    print(f'wind_avg: {wind_avg}')
    print(f'wind_max: {wind_max}')
    print(f'wind_min: {wind_min}')
    print(f'wind_direction: {wind_direction}')
    print(f'temperature: {temperature}')
    print(f'datetime: {datetime}')
    print(f'unixtime: {unixtime}')
