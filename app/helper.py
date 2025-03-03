# -*- coding: utf-8 -*-
# Using a closure function with enclosed state
def counter():
    count = 0  # Initial counter value

    def increment(reset=False):
        nonlocal count  # Use nonlocal to modify the outer variable
        if reset:
            count = 0
        else:
            count += 1
        return count

    return increment
