# -*- coding: utf-8 -*-
import os
import time
import sys
import schedule
import helper as hp
import yaml

# Load configuration from YAML file
def load_config():
    """
    

    Returns
    -------
    config : TYPE
        DESCRIPTION.

    """
    with open('config.yaml', 'r', encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config

# Use environment variables if they exist, otherwise fallback to the config file
def get_config_value(key, default=None):
    """
    

    Parameters
    ----------
    key : TYPE
        DESCRIPTION.
    default : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    env_value = os.getenv(key)
    if env_value:
        return env_value
    else:
        config = load_config()
    return config.get(key, default)

def run(windguru_api_call, fetch_email_addresses, logger):
    """
    

    Parameters
    ----------
    windguru_api_call : TYPE
        DESCRIPTION.
    fetch_email_addresses : TYPE
        DESCRIPTION.
    logger : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    try:
        # Get values from environment variables or config.yaml
        url1 = get_config_value("url1")
        url2 = get_config_value("url2")
        station_id = str(get_config_value("station_id"))
        interval = int(get_config_value("interval"))
        times_above_limit = int(get_config_value("timesAboveLimit"))
        times_below_limit = int(get_config_value("timesBelowLimit"))
        count_func = hp.counter()

        logger.info(f"Scheduled task with URL: {url2} and Interval: {interval}s")
    except Exception as ex:
        logger.error(f"Error fetching variable: {str(ex)}")
        sys.exit(1)  # Exit if we can't fetch the required configurations

    # Schedule the task once
    schedule.every(interval).seconds.do(windguru_api_call,
                                        url1=url1,
                                        url2=url2,
                                        station_id=station_id,
                                        times_above_limit=times_above_limit,
                                        times_below_limit=times_below_limit,
                                        count_func=count_func)

    schedule.every(300).seconds.do(fetch_email_addresses)

    logger.info("Scheduler started.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Wait for the next scheduled task to run
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        schedule.clear()  # Stop all tasks when CTRL+C is pressed
        logger.info("All tasks are stopped and exited.")
