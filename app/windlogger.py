# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 11:06:10 2025

@author: fub
"""
import logging
import sys
import io
import colorlog
from app import configuration as config

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set up the main logger
logger = logging.getLogger()
log_level = config.get_config_value("logLevel")

if not logger.hasHandlers():
    logger.setLevel(int(log_level))

    # Suppress noisy logs
    logging.getLogger("pymongo").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("schedule").setLevel(logging.WARNING)

    # 🎨 Custom log format with short time
    LOG_FORMAT = "%(log_color)s%(asctime)s - %(levelname)-8s %(emoji)s %(message)s%(reset)s"
    DATA_FORMAT = "%H:%M:%S"  # ⏰ Only Hours:Minutes:Seconds

    # 🔥 Log level colors
    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }

    # 🎭 Emojis for log levels
    emoji_map = {
        'DEBUG': '🐛',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }

    class EmojiFormatter(colorlog.ColoredFormatter):
        """Custom formatter to add emojis dynamically and pad level names."""
        def format(self, record):
            record.emoji = emoji_map.get(record.levelname, '')
            return super().format(record)

    # 🎨 Console handler (colored logs)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(int(log_level))
    console_formatter = EmojiFormatter(LOG_FORMAT, log_colors=log_colors, datefmt=DATA_FORMAT)
    console_handler.setFormatter(console_formatter)

    # 📜 File handler (no colors, short time format)
    file_handler = logging.FileHandler('./app.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s',
                                       datefmt=DATA_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
