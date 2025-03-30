from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
import threading
import time
from helper import store_collections_local_on_host
import requests
import scheduler
import database as db
import windlogger as wl
import configuration as config

# Global variable to track last email sent time
BELOW_MIN_WINDSPEED = 0  # Initialize as 0 (meaning no email sent yet)

# Create a lock to prevent overlap of tasks
task_lock = threading.Lock()

def store_daily_mongo():
    with task_lock:
        try:
            wl.logger.info('@@@@@@@@@ Store collections on local host @@@@@@@@@')
            result = store_collections_local_on_host
        except Exception as ex:
            wl.logger.critical('[{time.strftime("%H:%M:%S")}]: ' +
                               f'error while store collection on local host = {ex}')
        return result

def check_response_contains_param(response, station_id):
    try:
        if response['wind_avg'] is not None and response['wind_direction'] is not None:
            return True
    except Exception:
        wl.logger.warning(f'[{time.strftime("%H:%M:%S")}]: ' +
                          f'Station = [{station_id}] response doesnt contains AVG and DIRECTION')
    return False

def get_next_station_ids():
    client = db.connect_to_db(2000)
    station_entries = db.find_all_stations(client)
    station_ids = []
    for station in station_entries:
        station_ids.append(station['number'])
    return station_ids

def fetch_data_from_windguru(url1, url2, station_id):
    headers = {'Referer': f"{url1}{station_id}"}
    req = requests.get(f"{url2}{station_id}", headers=headers, timeout=5)
    return req

def windguru_api_call(url1, url2, station_ids, count_func, times_below_limit, times_above_limit):
    with task_lock:  # Only one task can run at a time
        req_tests = None
        wl.logger.debug("Starting windguru_api_call...")
        global BELOW_MIN_WINDSPEED
        counter_value = count_func()
        # Fetch all station_ids
        if station_ids is None:
            station_ids = get_next_station_ids()

        for station_id in station_ids:
            try:
                req = fetch_data_from_windguru(url1, url2, station_id)
                req_tests = req
                response = req.json()
                if not check_response_contains_param(response, station_id):
                    continue

                speed, direction = response['wind_avg'], response['wind_direction']
                wl.logger.info(f'[{time.strftime("%H:%M:%S")}]: Station [{station_id}] = ' +
                               f'Wind: {speed:.1f} m/s, {direction}°')
                wind_trigger = float(config.get_config_value("windspeedTrigger"))
                if speed > wind_trigger:
                    store_wind_data({
                        "name": "windguru-data",
                        "station": int(station_id), 
                        "speed": float(speed), 
                        "direction": int(direction), 
                        "ts": response['datetime'],
                        "temp": response['temperature']
                    })

                    if counter_value <= 1 and BELOW_MIN_WINDSPEED == 0:
                        send_email(
                            "Windguru Alert", "Wind speed has exceeded threshold", 
                            station_id,
                            speed
                            )
                    else:
                        wl.logger.info("Email blocked - Counter: %d", counter_value)
                        if counter_value >= times_above_limit:
                            count_func(reset=True)
                    BELOW_MIN_WINDSPEED = times_below_limit
                else:
                    if BELOW_MIN_WINDSPEED > 0:
                        BELOW_MIN_WINDSPEED -= 1
                    count_func(reset=True)

                wl.logger.debug("Data fetched successfully from %s at %s", f"{url2}{station_id}",
                                time.strftime('%H:%M:%S'))
                wl.logger.info("Counter: %d, Below Min Wind Speed Remaining: %d",
                               counter_value,
                               BELOW_MIN_WINDSPEED
                               )
            except Exception as ex:
                wl.logger.critical("Unexpected error in windguru_api_call: %s", ex, exc_info=True)
            finally:
                wl.logger.debug("Finished windguru_api_call")
        return req_tests

def store_wind_data(data):
    wl.logger.debug("Starting data insertion into MongoDB...")
    try:
        client = db.connect_to_db()
        db.insert_data(client, data)
    except Exception as ex:
        wl.logger.error("Error storing data in MongoDB: %s", ex, exc_info=True)
    finally:
        wl.logger.debug("Finished data insertion into MongoDB")

def fetch_email_addresses_for_station(station_id: int, current_wind_speed: float) -> list:
    email_list = []
    wl.logger.debug("Fetching email addresses...")
    try:
        client = db.connect_to_db()
        username_list = db.find_all_usernames_for_threshold_station(
            client,
            station_id,
            current_wind_speed
            )
        for username in username_list:
            user = db.find_user_by_username(client, username[0])
            if user == []:
                wl.logger.debug(f'User [{username}] not found')
            else:
                email_list.append(user.email)
    except Exception as ex:
        wl.logger.error("Error fetching email addresses: %s", ex, exc_info=True)
    finally:
        wl.logger.debug("Finished fetching email addresses")
    return email_list

def send_email(subject: str, body: str, station_id: int, current_wind_speed: float):
    mail_list = fetch_email_addresses_for_station(station_id, current_wind_speed)
    sender_email = "elbeato.furrer@gmail.com"
    app_password = "uqzvthsdfbucolnp"  # Replace with environment variable!

    if not mail_list:
        wl.logger.warning(f'⚠️ No email addresses found for station {station_id}')
        return

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(mail_list)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    #context = ssl.create_default_context()
    context = ssl._create_unverified_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, ", ".join(mail_list), msg.as_string())
            wl.logger.info(f'✅ Email sent successfully to [{", ".join(mail_list)}]')
    except Exception as ex:
        wl.logger.error("❌ Failed to send email: %s", ex, exc_info=True)

def serialize_user(user):
    """Convert MongoDB ObjectId to string and prepare other fields."""
    user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return user

if __name__ == '__main__':
    # restore current mongo situation after program start
    store_daily_mongo()
    scheduler.run(wl.logger, windguru_api_call, store_collections_local_on_host)
