"""LED control module"""
from .controller import LEDController
from src.utils.logger import Logger

log = Logger()
log.debug("Initializing LED module")

__all__ = ["LEDController"]
