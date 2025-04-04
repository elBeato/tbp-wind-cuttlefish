# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
import logging
import sys
import io
import configuration as config

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set up logging with both console and file handlers
logger = logging.getLogger()
log_level = config.get_config_value("logLevel")

# Check if handlers are already added to prevent duplicates
# DEBUG (lowest severity) = 10
# INFO = 20
# WARNING = 30
# ERROR
# CRITICAL (highest severity)

if not logger.hasHandlers():
    logger.setLevel(int(log_level))  # Log level for both handlers
    # Suppress MongoDB Connection Details Specifically
    logging.getLogger("pymongo").setLevel(logging.ERROR)  # Show only critical issues
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # Suppress HTTP connection logs
    logging.getLogger("asyncio").setLevel(logging.WARNING)  # Reduce asyncio noise
    logging.getLogger("schedule").setLevel(logging.INFO)
    # Suppress DEBUG logs from the `schedule` library
    logging.getLogger("schedule").setLevel(logging.WARNING)

    # Console handler - logs to the console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(int(log_level))

    # File handler - logs to a file inside the container
    file_handler = logging.FileHandler('./app.log')
    file_handler.setLevel(logging.DEBUG)

    # Define a log format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    file_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.info("LOGGER: Container=INFO, File- and console=DEBUG")
