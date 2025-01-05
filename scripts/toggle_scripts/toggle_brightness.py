#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.logger import Logger
from src.core.config import Config

log = Logger()
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config', 'settings.json')

def toggle_brightness():
    try:
        config = Config()
        
        log.debug("Reading current brightness configuration")
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError("Configuration file not found")
            
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            
        display_config = data.get('display', {})
        current = display_config.get('brightness', 4)
        levels = display_config.get('brightness_levels', {}).get('display', [2, 4, 7])
        
        next_level = levels[(levels.index(current) + 1) % len(levels)]
        log.info(f"Changing brightness from {current} to {next_level}")
        
        if 'display' not in data:
            data['display'] = {}
        data['display']['brightness'] = next_level
        
        temp_file = Path(CONFIG_FILE).with_suffix('.json.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        os.replace(temp_file, CONFIG_FILE)
        
        trigger_file = os.path.join(PROJECT_ROOT, 'config', '.update_trigger')
        Path(trigger_file).touch()
        
        log.ok(f"Brightness updated to {next_level}")
            
    except Exception as e:
        log.error(f"Failed to toggle brightness: {e}")
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        sys.exit(1)

if __name__ == "__main__":
    toggle_brightness()
