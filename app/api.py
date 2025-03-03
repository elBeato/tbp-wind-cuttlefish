import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import database as db
import threading
import scheduler
import windlogger as wl
import time

# Global variable to track last email sent time
BELOW_MIN_WINDSPEED = 0  # Initialize as 0 (meaning no email sent yet)

# Create a lock to prevent overlap of tasks
task_lock = threading.Lock()

def windguru_api_call(url1, url2, station_id, count_func, times_below_limit, times_above_limit):
    with task_lock:  # Only one task can run at a time
        wl.logger.debug("Starting windguru_api_call...")
        global BELOW_MIN_WINDSPEED
        counter_value = count_func()
        try:
            headers = {'Referer': f"{url1}{station_id}"}
            req = requests.get(f"{url2}{station_id}", headers=headers, timeout=5)
            response = req.json()
            speed, direction = response['wind_avg'], response['wind_direction']

            wl.logger.info("[%s] Wind: %.1f m/s, %.1f°", time.strftime('%H:%M:%S'), speed, direction)

            if speed > 2.0:
                store_wind_data({
                    "station": station_id, 
                    "speed": speed, 
                    "direction": direction, 
                    "ts": response['datetime'],
                    "temp": response['temperature']
                })

                if counter_value <= 1 and BELOW_MIN_WINDSPEED == 0:
                    send_email("Windguru Alert", "Wind speed has exceeded 2.0 m/s.")
                else:
                    wl.logger.info("Email blocked - Counter: %d", counter_value)
                    if counter_value >= times_above_limit:
                        count_func(reset=True)
                BELOW_MIN_WINDSPEED = times_below_limit
            else:
                if BELOW_MIN_WINDSPEED > 0:
                    BELOW_MIN_WINDSPEED -= 1
                count_func(reset=True)

            wl.logger.debug("Data fetched successfully from %s at %s", f"{url2}{station_id}", time.strftime('%H:%M:%S'))
            wl.logger.info("Counter: %d, Below Min Wind Speed Remaining: %d", counter_value, BELOW_MIN_WINDSPEED)
        except requests.RequestException as ex:
            wl.logger.error("Failed to fetch data from %s: %s", f"{url2}{station_id}", ex)
        except Exception as e:
            wl.logger.critical("Unexpected error in windguru_api_call: %s", e, exc_info=True)
        finally:
            wl.logger.debug("Finished windguru_api_call")
        return req

def store_wind_data(data):
    with task_lock:
        wl.logger.debug("Starting data insertion into MongoDB...")
        try:
            mongo_client = db.connect_to_db("Windseeker", "StationData")
            user_collection = db.connect_to_collection(mongo_client, "Windseeker", "StationData")
            db.insert_data(user_collection, data)
        except Exception as ex:
            wl.logger.error("Error storing data in MongoDB: %s", ex, exc_info=True)
        finally:
            wl.logger.debug("Finished data insertion into MongoDB")

def fetch_email_addresses():
    with task_lock:
        wl.logger.debug("Fetching email addresses...")
        try:
            mongo_client = db.connect_to_db("Windseeker", "Users")
            user_collection = db.connect_to_collection(mongo_client, "Windseeker", "Users")
            db.insert_user(user_collection)
            for user in db.find_all(user_collection):
                wl.logger.debug("Fetched user: %s", user)
        except Exception as ex:
            wl.logger.error("Error fetching email addresses: %s", ex, exc_info=True)
        finally:
            wl.logger.debug("Finished fetching email addresses")

def send_email(subject, body):
    sender_email = "elbeato.furrer@gmail.com"
    receiver_email = "beat.furrer@sisag.ch"
    app_password = "uqzvthsdfbucolnp"  # Replace with environment variable!

    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = sender_email, receiver_email, subject
    msg.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            wl.logger.info("✅ Email sent successfully to %s", receiver_email)
    except Exception as e:
        wl.logger.error("❌ Failed to send email: %s", e, exc_info=True)

if __name__ == '__main__':
    scheduler.run(windguru_api_call, fetch_email_addresses, wl.logger)
