# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
import app.helper as hp

def test_counter():
    count_func = hp.counter()
    assert count_func() == 1
