# -*- coding: utf-8 -*-
import os
import yaml
from dotenv import load_dotenv

# Load configuration from YAML file
def load_config():
    try:
        with open('../config.yaml', 'r', encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return config
    except yaml.YAMLError as e:
        print(f"Error loading YAML: {e}")
        return {}

# Use environment variables if they exist, otherwise fallback to the config file
# Envirement variables are accessable in docker-compose file or fix in YAML file
def get_config_value(key, default=None):
    load_dotenv()
    env_value = os.getenv(key)
    if env_value:
        return env_value

    config = load_config()
    return config.get(key, default)
