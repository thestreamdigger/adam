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

def toggle_display_mode():
    config = read_config()
    
    current_mode = config.get('display', {}).get('mode', 'remaining')
    new_mode = "elapsed" if current_mode == "remaining" else "remaining"

    config.setdefault('display', {})['mode'] = new_mode
    write_config(config)

if __name__ == "__main__":
    toggle_display_mode()
