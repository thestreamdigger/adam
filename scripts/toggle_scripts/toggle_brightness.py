import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config', 'settings.json')

def read_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error reading configuration: {e}", file=sys.stderr)
        sys.exit(1)

def write_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving configuration: {e}", file=sys.stderr)
        sys.exit(1)

def toggle_brightness():
    config = read_config()
    
    current = config.get('display', {}).get('brightness', 2)
    if current >= 6:
        new_brightness = 0
    elif current >= 2:
        new_brightness = 6
    else:
        new_brightness = 2

    config.setdefault('display', {})['brightness'] = new_brightness
    write_config(config)

if __name__ == "__main__":
    toggle_brightness()
