import json
import os
from src.utils.logger import Logger

log = Logger()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            log.debug("Initializing configuration manager")
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.config_path = os.path.join(base_path, 'config', 'settings.json')
            self.config = {}
            self.load_config()
            log.configure(self.config)
            log.ok("Configuration manager initialized")
            self.initialized = True

    def load_config(self):
        try:
            log.debug(f"Loading configuration from {self.config_path}")
            if not os.path.exists(self.config_path):
                log.warning("Configuration file not found, using defaults")
                self.config = {}
                return

            with open(self.config_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    log.warning("Empty configuration file, using defaults")
                    self.config = {}
                    return
                
                self.config = json.loads(content)
                log.ok("Configuration loaded successfully")
            
        except Exception as e:
            log.error(f"Failed to load configuration: {e}")
            self.config = {}

    def get(self, key, default=None):
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except:
            return default
