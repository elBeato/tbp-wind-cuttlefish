# -*- coding: utf-8 -*-
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager

options = webdriver.EdgeOptions()
options.add_argument("--headless")  # Run in the background
options.add_argument("--disable-gpu")  # Disable GPU acceleration (Windows fix)
options.add_argument("--no-sandbox")  # Recommended for Linux systems
options.add_argument("--disable-dev-shm-usage")  # Prevent crashes in Docker/Linux
# DOM is ready but external resources (images) are still loading
options.page_load_strategy = "eager"

# Set up the WebDriver (make sure to have ChromeDriver installed)
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

error_stations = [ 13158 ]

# URL of the station page
URL = "https://www.windguru.cz/station/"
my_dict = {}
print(f'################# START AT {datetime.now().time()} #################')
for n in error_stations:
    # Open the page
    driver.get(URL + str(n))

    # Wait for the page to fully load (you can adjust the sleep time if needed)
    time.sleep(0.8)

    # Find the station name by its class inside the <span> element
    station_name = driver.find_element(By.CSS_SELECTOR,
                                       "span.wgs_station_name.spotname-truncate").text

    # Print the station name
    my_dict[n] = f"St: {n:06d}; {station_name}"

    if n % 100 == 0:
        now = datetime.now()
        print(f"{now.time()}: current position: {n}")

# Close the browser
driver.quit()

print(f'################# STOPPED AT {datetime.now().time()} #################')

with open('output_error_stations_2.txt', 'w', encoding='utf-8') as file:
    # Iterate through the dictionary and write each key-value pair on a new line
    for key, value in my_dict.items():
        file.write(f'{value}\n')
