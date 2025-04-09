from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
import threading
import time
from app.helper import fetch_data_from_windguru, get_next_station_ids, check_response_contains_param
from app.helper import store_collections_local_on_host
from app import scheduler
from app import database as db
from app import windlogger as wl
from app import configuration as config
from app.models import DataModel

# Global variable to track last email sent time
BELOW_MIN_WIND_SPEED = {station: 0 for station in range(15500)}

# Create a lock to prevent overlap of tasks
task_lock = threading.Lock()

def daily_store_mongo():
    with task_lock:
        try:
            wl.logger.info('@@@@@@@@@@@@@@@@@@  Store collections on local host @@@@@@@@@@@@@@@@@@')
            result = store_collections_local_on_host
        except Exception as ex:
            wl.logger.critical('[{time.strftime("%H:%M:%S")}]: ' +
                               f'error while store collection on local host = {ex}')
        return result

def windguru_api_call(
        url1: str,
        url2: str,
        station_ids: list,
        counters: dict,
        times_below_limit: int,
        times_above_limit: int):
    with task_lock:  # Only one task can run at a time
        req_tests = None
        wl.logger.debug(
            "----------------------- Starting new windspeed check -----------------------"
            )

        # Fetch all station_ids
        if station_ids is None:
            station_ids = get_next_station_ids()

        for station_id in station_ids:
            try:
                wl.logger.info(f'Station[{station_id}] - Starting windguru_api_call... ')
                req = fetch_data_from_windguru(url1, url2, station_id)
                req_tests = req
                response = req.json()
                if not check_response_contains_param(response, station_id):
                    continue
                result = wind_speed_excess(
                    response,
                    station_id,
                    counters,
                    times_below_limit,
                    times_above_limit
                    )
                if result:
                    wl.logger.debug(f'Station[{station_id}] - '+
                                    f'Data fetched successfully from {url2}{station_id} '+
                                    f'at {time.strftime("%H:%M:%S")}')
                wl.logger.info(f'Counter: {counters[station_id]}, times below min speed: '+
                               '{BELOW_MIN_WIND_SPEED[station_id]}')
            except Exception as ex:
                wl.logger.critical(f'Station[{station_id}] - '+
                                   f'Unexpected error in windguru_api_call: {ex}')
        return req_tests

def wind_speed_excess(
        response: str,
        station_id: int,
        counters: dict,
        times_below_limit: int,
        times_above_limit: int,
        ) -> bool:

    station_counter = counters[station_id]
    speed, direction = float(response['wind_avg']), float(response['wind_direction'])
    timestamp, temperature = response['datetime'], float(response['temperature'])

    # Connect to threshold collection and find the lowest threshold
    client = db.connect_to_db()
    wind_trigger = db.find_lowest_threshold_for_station(client, station_id)

    wl.logger.info(f'[{time.strftime("%H:%M:%S")}]: Station [{station_id}] = ' +
                   f'Wind: {speed:.1f} m/s, {direction}° and min wind_trigger: {wind_trigger} m/s')

    if speed > wind_trigger:
        wind_data = {
            "name": "Windguru-data",
            "station": int(station_id), 
            "speed": float(speed), 
            "direction": int(direction), 
            "ts": timestamp,
            "temp": temperature
        }
        data = DataModel(**wind_data)
        store_wind_data(data)
        if station_counter <= 0 and BELOW_MIN_WIND_SPEED[station_id] == 0:
            send_email(
                'Windguru Alert for station: ', 
                station_id,
                speed
                )
        else:
            wl.logger.debug(f'Station[{station_id}] - '+
                            f'Email blocked because of counter={station_counter}')
            if station_counter >= times_above_limit:
                counters[station_id] = 0
            else:
                counters[station_id] += 1
        BELOW_MIN_WIND_SPEED[station_id] = times_below_limit
        return True

    wl.logger.debug(f'Station[{station_id}]- '+
                    f'Email blocked because of speed < wind_trigger: {speed} < {wind_trigger}')
    if BELOW_MIN_WIND_SPEED[station_id] > 0:
        BELOW_MIN_WIND_SPEED[station_id] -= 1
    counters[station_id] = 0
    return False

def store_wind_data(data: DataModel):
    try:
        client = db.connect_to_db()
        db.insert_data(client, data)
    except Exception as ex:
        wl.logger.error(f'Station[{data.station}] - Error storing data in MongoDB: {ex}')

def fetch_email_addresses_for_station(station_id: int, current_wind_speed: float) -> list:
    email_list = []
    wl.logger.debug(f'Station[{station_id}] - Fetching email addresses...')
    try:
        client = db.connect_to_db()
        username_list = db.find_all_usernames_for_threshold_station(
            client,
            station_id,
            current_wind_speed
            )
        for username in username_list:
            user = db.find_user_by_username(client, username[0])
            if not user:
                wl.logger.debug(f'Station[{station_id}] - User [{username}] not found')
            else:
                email_list.append(user.email)
    except Exception as ex:
        wl.logger.error(f'Station[{station_id}] - Error fetching email addresses: {ex}')
    return email_list

def send_email(subject: str, station_id: int, current_wind_speed: float):
    mail_list = fetch_email_addresses_for_station(station_id, current_wind_speed)
    sender_email = "elbeato.furrer@gmail.com"
    app_password = config.get_config_value("GOOGLE_APP_PASSWORD")

    if not mail_list:
        wl.logger.warning(f'Station[{station_id}] - '+
                          f'No email addresses found for station {station_id}')
        return
    client = db.connect_to_db()
    station = db.find_station_id(client, station_id)
    body = f'The wind speed of the station {station[0]["name"]} is above its limit value. '

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(mail_list)
    msg["Subject"] = f'{station[0]["name"]}: ' + subject
    msg.attach(MIMEText(body, "plain"))

    #context = ssl.create_default_context()
    context = ssl._create_unverified_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, ", ".join(mail_list), msg.as_string())
            wl.logger.info(f'Station[{station_id}] - '+
                           f'Email sent successfully to [{", ".join(mail_list)}]')
    except Exception as ex:
        wl.logger.error(f'Station[{station_id}] - Failed to send email: {ex}')

def serialize_user(user):
    """Convert MongoDB ObjectId to string and prepare other fields."""
    user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return user

if __name__ == '__main__':
    # restore current mongo situation after program start
    daily_store_mongo()
    scheduler.run(wl.logger, windguru_api_call, store_collections_local_on_host)
