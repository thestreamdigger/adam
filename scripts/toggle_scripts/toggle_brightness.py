#!/usr/bin/env python3
import json
import os
import sys

# Adiciona o diretório raiz do projeto ao Python Path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.logger import Logger

log = Logger()

CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config', 'settings.json')

def read_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        log.error(f"Error reading configuration: {e}")
        sys.exit(1)

def write_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        log.error(f"Error saving configuration: {e}")
        sys.exit(1)

def toggle_brightness():
    log.debug("Reading current brightness configuration")
    config = read_config()
    
    current = config.get('display', {}).get('brightness', 2)
    if current >= 6:
        new_brightness = 0
    elif current >= 2:
        new_brightness = 6
    else:
        new_brightness = 2

    log.info(f"Changing brightness from {current} to {new_brightness}")
    config.setdefault('display', {})['brightness'] = new_brightness
    write_config(config)
    log.ok("Brightness updated successfully")

if __name__ == "__main__":
    toggle_brightness()
