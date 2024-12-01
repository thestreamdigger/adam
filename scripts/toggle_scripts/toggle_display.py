import json
import os
import sys

# Correct path to the settings.json configuration file
CONFIG_FILE = '/home/pi/adam2/config/settings.json'

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

def toggle_display_mode():
    """Toggle the display mode between 'elapsed' and 'remaining' in the configuration."""
    config = read_config()
    
    # Toggle display modes
    current_mode = config.get('display', {}).get('mode', 'remaining')
    new_mode = "elapsed" if current_mode == "remaining" else "remaining"

    # Update configuration
    config.setdefault('display', {})['mode'] = new_mode
    write_config(config)

if __name__ == "__main__":
    toggle_display_mode()
