#!/usr/bin/env python3
import json
import os
import sys

# Correct path to the settings.json configuration file
CONFIG_FILE = '/home/pi/adam/config/settings.json'

def read_config():
    """Read the current configuration from the JSON file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error reading configuration: {e}", file=sys.stderr)
        sys.exit(1)

def write_config(config):
    """Write the updated configuration back to the JSON file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving configuration: {e}", file=sys.stderr)
        sys.exit(1)

def toggle_brightness():
    """Toggle brightness levels (0 -> 2 -> 6 -> 0) in the configuration."""
    config = read_config()
    
    # Toggle brightness levels
    current = config.get('display', {}).get('brightness', 2)
    if current >= 6:
        new_brightness = 0
    elif current >= 2:
        new_brightness = 6
    else:
        new_brightness = 2

    # Update configuration
    config.setdefault('display', {})['brightness'] = new_brightness
    write_config(config)

if __name__ == "__main__":
    toggle_brightness()
