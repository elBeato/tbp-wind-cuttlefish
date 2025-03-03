# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:20 2025

@author: fub
"""
import app.Helper as hp

def test_counter():
    x = hp.counter()
    assert x() == 1