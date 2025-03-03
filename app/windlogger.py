# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
import logging

# Set up logging with both console and file handlers
logger = logging.getLogger()

# Check if handlers are already added to prevent duplicates
# DEBUG (lowest severity)
# INFO
# WARNING
# ERROR
# CRITICAL (highest severity)

if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)  # Log level for both handlers

    # Console handler - logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # File handler - logs to a file inside the container
    file_handler = logging.FileHandler('./app.log')
    file_handler.setLevel(logging.INFO)

    # Define a log format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Apply the formatter to both handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
