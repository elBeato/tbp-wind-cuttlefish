# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
import api as api
import helper as hp

def test_call_windguru_api():
    stationId = 2736
    count_func = hp.counter()
    req = api.windguru_api_call(
        'https://www.windguru.cz/station/', 
        'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=', 
        stationId, 
        count_func, 
        30, 
        90
    )
    assert req.url == "https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station=" + str(stationId)
    assert req.status_code == 200
    assert req.encoding == 'utf-8'
    assert req.content != None
    assert req.content != {}

    