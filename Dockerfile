# Use the official Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and config.yaml from the 'app' folder into the container
COPY app/API.py /app/API.py
COPY app/config.yaml /app/config.yaml

# Install required Python packages
RUN pip install --no-cache-dir requests schedule pyyaml

# Run the Python script
CMD ["python", "API.py"]
