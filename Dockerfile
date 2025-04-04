# Use the official Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and config.yaml from the 'app' folder into the container
COPY app/configuration.py /app/configuration.py
COPY app/models.py /app/models.py
COPY app/startup.py /app/startup.py
COPY app/database.py /app/database.py
COPY app/helper.py /app/helper.py
COPY app/scheduler.py /app/scheduler.py
COPY app/windlogger.py /app/windlogger.py
COPY app/api.py /app/api.py
COPY config.yaml /config.yaml

# Install cert for SSL
RUN pip3 install pydantic[email] dotenv

# Install required Python packages
RUN pip3 install --no-cache-dir flask flasgger flask_cors requests schedule pyyaml pymongo pytest bcrypt pydantic

# Install CA certificates for SSL
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# Expose the API port
EXPOSE 5050

# Start both scripts using a shell process
CMD ["sh", "-c", "python startup.py & python api.py"]
