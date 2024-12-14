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

def toggle_display_mode():
    log.debug("Reading current display mode configuration")
    config = read_config()
    
    current_mode = config.get('display', {}).get('mode', 'remaining')
    new_mode = "elapsed" if current_mode == "remaining" else "remaining"

    log.info(f"Changing display mode from {current_mode} to {new_mode}")
    config.setdefault('display', {})['mode'] = new_mode
    write_config(config)
    log.ok("Display mode updated successfully")

if __name__ == "__main__":
    toggle_display_mode()
