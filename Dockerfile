# Use the official Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and config.yaml from the 'app' folder into the container
COPY app/API.py /app/API.py
COPY app/Database.py /app/Database.py
COPY app/Helper.py /app/Helper.py
COPY app/Scheduler.py /app/Scheduler.py
COPY app/WindLogger.py /app/WindLogger.py
COPY app/config.yaml /app/config.yaml

# Install required Python packages
RUN pip install --no-cache-dir requests schedule pyyaml pymongo

# Run the Python script
CMD ["python", "API.py"]
