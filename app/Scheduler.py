# -*- coding: utf-8 -*-
import yaml
import os
import app.Helper as hp
import schedule
import time

# Load configuration from YAML file
def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config

# Use environment variables if they exist, otherwise fallback to the config file
def get_config_value(key, default=None):
    env_value = os.getenv(key)
    if env_value:
        return env_value
    else:
        config = load_config()
        return config.get(key, default)

def run(windguru_api_call, fetch_email_addresses, logger):
    try:
        # Get values from environment variables or config.yaml
        url1 = get_config_value("url1")
        url2 = get_config_value("url2")
        stationId = str(get_config_value("stationId"))
        interval = int(get_config_value("interval"))
        timesAboveLimit = int(get_config_value("timesAboveLimit"))
        timesBelowLimit = int(get_config_value("timesBelowLimit"))
        count_func = hp.counter()
        
        logger.info(f"Scheduled task with URL: {url2} and Interval: {interval}s")
    except Exception as e: 
        logger.error(f"Error fetching variable: {str(e)}")
        exit(1)  # Exit if we can't fetch the required configurations

    # Schedule the task once
    schedule.every(interval).seconds.do(windguru_api_call, 
                                        url1=url1, 
                                        url2=url2, 
                                        stationId=stationId, 
                                        timesAboveLimit=timesAboveLimit,
                                        timesBelowLimit=timesBelowLimit,
                                        count_func=count_func)
    
    #schedule.every(5).seconds.do(fetch_email_addresses)
    
    logger.info("Scheduler started.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Wait for the next scheduled task to run
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        schedule.clear()  # Stop all tasks when CTRL+C is pressed
        logger.info("All tasks are stopped and exited.")