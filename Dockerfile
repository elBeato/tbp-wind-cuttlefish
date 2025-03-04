# Use the official Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and config.yaml from the 'app' folder into the container
COPY app/api.py /app/api.py
COPY app/database.py /app/database.py
COPY app/helper.py /app/helper.py
COPY app/scheduler.py /app/scheduler.py
COPY app/windlogger.py /app/windlogger.py
COPY app/config.yaml /app/config.yaml
COPY app/windseekerapi.yaml /app.windseekerapi.yaml
COPY app/configuration.yaml /app.configuration.yaml

# Install required Python packages
RUN pip install --no-cache-dir requests schedule pyyaml pymongo pytest

# Run the Python script
CMD ["python", "api.py"]
