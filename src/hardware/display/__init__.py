from .tm1637 import TM1637
from src.utils.logger import Logger

log = Logger()
log.debug("Initializing display module")

__all__ = ["TM1637"]
