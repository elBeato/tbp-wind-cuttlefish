# 🌬️ tbp-wind-cuttlefish 💨
💥 Scrapper for windguru stations with API. Run as Docker Container possible.

[![Python application](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/python-app.yml)
[![Pylint](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/pylint.yml)
[![Docker Image CI](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/docker-image.yml)

# 🧰 Functions
- Call windguru api for data
- Send mail to subscribers

# ⚙️ Configuration
- Interval: Number of times in seconds when the API will called
- TimesAboveLimit: How many interval must be above limit until another email get triggered
- WindLimit: Value for receiving an email 

# 🧑‍💻 Contribution
Warmly wellcome ... 

## Install IDE
Working with Spyder 6.0 via anaconda

## Install tests
Install Run unit test: conda install -c spyder-ide spyder-unittest
In the Run menu, select Run unit tests. If you do not see this menu item, then the plugin is not installed.
Install pytest: conda install pytest
