import requests
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import Database as db
import threading
import Scheduler

# Global variable to track last email sent time
below_min_windspeed = 0  # Initialize as 0 (meaning no email sent yet)

# Create a lock to prevent overlap of tasks
task_lock = threading.Lock()

# Set up logging with both console and file handlers
logger = logging.getLogger()

# Check if handlers are already added to prevent duplicates
#DEBUG (lowest severity)
#INFO
#WARNING
#ERROR
#CRITICAL (highest severity)

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

def windguru_api_call(url1, url2, stationId, count_func, timesBelowLimit, timesAboveLimit):
    with task_lock:  # Only one task can run at a time
        logger.debug("Starting \"windguru_api_call\" .... ")
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
        finally:
            logger.debug("Finished \"windguru_api_call\"!")


def fetch_email_addresses():
    with task_lock:  # Prevent task_2 from running while windguru_api_call is running
        logger.debug("Starting \"fetch_email_addresses\" .... ")
        try:
            mongoClient = db.connect_to_db("Windseeker", "Users")
            userCollection = db.connect_to_user_collection(mongoClient, "Windseeker", "Users")
            
            db.insert_user(userCollection)
            
            for u in db.find_all(userCollection):
                print(u) 
                
        except Exception as e:
            logger.error(f"Error fetching variable: {str(e)}")
        finally: 
            logger.debug("Finished \"fetch_email_addresses\"!")


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
    Scheduler.run(windguru_api_call, fetch_email_addresses,logger)
    

