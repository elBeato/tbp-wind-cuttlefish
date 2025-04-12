# 🌬️ tbp-wind-cuttlefish 💨
💥 Scrapper for windguru stations with API. Run as Docker Container possible.

A microservices architecture with a Python-based containerized backend (Flask, scraping, and business logic services), a Next.js frontend, and MongoDB for persistence. Backend configuration follows 12-factor principles and is tested using Pytest.

[![Python application](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/python-app.yml)
[![Pylint](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/pylint.yml)
[![Docker Image CI](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/elBeato/tbp-wind-cuttlefish/actions/workflows/docker-image.yml)

# 🧰 Functions
- Call windguru api for data (on request)
- Check for online data on all windguru stations (daily)
- Send mail to subscribers depending on wind speed threshold

# Architecture
It is Microservices-Based architecture, where in the frontend
is NEXT.js and in the backend Python. 
![Architecture.png](imgs/Architecture.png)
## 🧩 Component Breakdown:
### Frontend:
Technology: Next.js (React-based framework)

Role: SSR (Server-Side Rendering), client interaction, UI rendering.

### Backend (Microservices, containerized):

#### API Container (Flask):

Acts as the public-facing REST API.

Interfaces directly with the frontend.

#### Subscriber Container:

Handles business logic.

Acts as a worker or service that communicates with external APIs (Windguru).

#### Helper Container:

Scrapes live data (online stations) and makes it available to other services.

### Database:
MongoDB (likely accessed by multiple containers, probably by the Subscriber and Helper for data persistence)


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

# Run docker
Run the docker containers with the following commands

Build: ``docker compose build``

Start: ``docker compose --env-file .env.prod up -d``

Check if all containers are running: ``docker ps``