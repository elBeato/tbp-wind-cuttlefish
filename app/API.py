import requests
import schedule
import time
import yaml
import os
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Global variable to track last email sent time
below_min_windspeed = 0  # Initialize as 0 (meaning no email sent yet)

# Set up logging with both console and file handlers
logger = logging.getLogger()

# Check if handlers are already added to prevent duplicates
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

def my_task(url1, url2, stationId, count_func, timesBelowLimit, timesAboveLimit):
    global below_min_windspeed
    counter_value = count_func()  # Increment the counter every time call the function
    try: 
        headers = {'Referer': url1 + str(stationId)}
        r = requests.get(url2 + str(stationId), headers=headers).json()
        
        speed = r['wind_avg']
        direction = r['wind_direction']
        
        text = f"[{time.strftime('%H:%M:%S')}] Wind-Speed: {speed:.1f}, Direction: {direction:.1f}"
        
        if speed > 2.0:
            if counter_value <= 1 and below_min_windspeed == 0:
                send_email(text, "Windguru")
            else:
                logger.info(f"Email message is blocked because counter-Value: {str(counter_value)}")
                if (counter_value >= timesAboveLimit):
                    count_func(reset=True)
            below_min_windspeed = timesBelowLimit
        else:
            if (below_min_windspeed > 0):
                below_min_windspeed = below_min_windspeed - 1
            count_func(reset=True)
            
        logger.debug(f"Task fetched data from {url2 + str(stationId)} at {time.strftime('%H:%M:%S')}")
        logger.info(text)
        logger.info(f"Counter value: {str(counter_value)} and {str(below_min_windspeed)} times below the min windspeed of 12km/h")
    except Exception as e:
        logger.error(f"Error fetching data from {url2}: {str(e)}")

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


def send_email(subject, body):
    sender_email = "elbeato.furrer@gmail.com"
    receiver_email = "beat.furrer@sisag.ch"  
    app_password = "uqzvthsdfbucolnp"  # Load App Password from environment variable

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach the email body
    msg.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)  # Use the App Password
            server.sendmail(sender_email, receiver_email, msg.as_string())
            logger.info("✅ Email sent successfully.")
    except Exception as e:
        logger.info(f"❌ Failed to send email: {e}")

if __name__ == '__main__':
    try:
        # Get values from environment variables or config.yaml
        url1 = get_config_value("url1")
        url2 = get_config_value("url2")
        stationId = str(get_config_value("stationId"))
        interval = int(get_config_value("interval"))
        timesAboveLimit = int(get_config_value("timesAboveLimit"))
        timesBelowLimit = int(get_config_value("timesBelowLimit"))
        count_func = counter()
        
        logger.info(f"Scheduled task with URL: {url2} and Interval: {interval}s")
    except Exception as e: 
        logger.error(f"Error fetching variable: {str(e)}")
        exit(1)  # Exit if we can't fetch the required configurations

    # Schedule the task once
    schedule.every(interval).seconds.do(my_task, 
                                        url1=url1, 
                                        url2=url2, 
                                        stationId=stationId, 
                                        timesAboveLimit=timesAboveLimit,
                                        timesBelowLimit=timesBelowLimit,
                                        count_func=count_func)
    logger.info("Scheduler started.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Wait for the next scheduled task to run
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        schedule.clear()  # Stop all tasks when CTRL+C is pressed
        logger.info("All tasks are stopped and exited.")
