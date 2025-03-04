# -*- coding: utf-8 -*-
import os
import yaml

# Load configuration from YAML file
def load_config():
    with open('config.yaml', 'r', encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config

# Use environment variables if they exist, otherwise fallback to the config file
# Envirement variables are accessable in docker-compose file or fix in YAML file
def get_config_value(key, default=None):
    env_value = os.getenv(key)
    if env_value:
        return env_value

    config = load_config()
    return config.get(key, default)
