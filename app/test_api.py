# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
import api
import helper as hp

def test_call_windguru_api():
    station_id = 2736
    count_func = hp.counter()
    req = api.windguru_api_call(
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
