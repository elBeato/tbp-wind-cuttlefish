# -*- coding: utf-8 -*-
import time
import sys
import schedule
from app import configuration as config

def run(logger, windguru_api_call, store_collections_local_on_host):
    try:
        # Get values from environment variables or config.yaml
        url1 = config.get_config_value("url1")
        url2 = config.get_config_value("url2")
        interval = int(config.get_config_value("INTERVAL"))
        times_below_limit = int(config.get_config_value("TIMES_BELOW_LIMIT"))
        times_above_limit = int(config.get_config_value("TIMES_ABOVE_LIMIT"))

        logger.info("#######################  start app  #######################")
        logger.info(f"Scheduled task with URL: {url2} and Interval: {interval}s")
    except Exception as ex:
        logger.error(f"Error fetching environment variables: {str(ex)}")
        sys.exit(1)  # Exit if we can't fetch the required configurations

    counters_above = {station: 0 for station in range(15500)}
    counters_below = {station: 0 for station in range(15500)}

    # Schedule the task once
    schedule.every(interval).seconds.do(windguru_api_call,
                                        url1=url1,
                                        url2=url2,
                                        station_ids=None,
                                        counters_above=counters_above,
                                        counters_below=counters_below,
                                        times_above_limit=times_above_limit,
                                        times_below_limit=times_below_limit)

    schedule.every(1).day.do(store_collections_local_on_host)

    logger.info("Scheduler started.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Wait for the next scheduled task to run
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        schedule.clear()  # Stop all tasks when CTRL+C is pressed
        logger.info("All tasks are stopped and exited.")
