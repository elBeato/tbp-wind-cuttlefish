# Use the official Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /project-root

# Set PYTHONPATH to allow absolute imports
ENV PYTHONPATH=/project-root

# Copy the source backup
COPY app/ /project-root/app/
COPY config.yaml /config.yaml

# Install CA certificates for SSL
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip3 install --no-cache-dir \
    flask flasgger flask_cors \
    requests schedule pyyaml pymongo pytest bcrypt \
    pydantic[email] \
    python-dotenv colorlog \
    gunicorn

# Expose the API port
EXPOSE 5050

# Start the app using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "app.api:app"]

