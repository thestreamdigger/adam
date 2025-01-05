#!/usr/bin/env python3
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from service.player_service import PlayerService
from utils.logger import Logger

log = Logger()

def print_banner():
    banner = """
 ▗▄▖    ▐▌▗▞▀▜▌▄▄▄▄      ▗▞▀▀▘▄▄▄   ▄▄▄     ▗▖  ▗▖ ▄▄▄   ▗▄▖    ▐▌▗▞▀▚▖
▐▌ ▐▌   ▐▌▝▚▄▟▌█ █ █     ▐▌  █   █ █        ▐▛▚▞▜▌█   █ ▐▌ ▐▌   ▐▌▐▛▀▀▘
▐▛▀▜▌▗▞▀▜▌     █   █     ▐▛▀▘▀▄▄▄▀ █        ▐▌  ▐▌▀▄▄▄▀ ▐▌ ▐▌▗▞▀▜▌▝▚▄▄▖
▐▌ ▐▌▝▚▄▟▌               ▐▌                 ▐▌  ▐▌      ▝▚▄▞▘▝▚▄▟▌     
                                                                       
Version 2.0.0 (2025) - Streamdigger
"""
    return banner

def main():
    print(print_banner())
    
    try:
        log.wait("Initializing player service")
        service = PlayerService()
        log.ok("Player service is ready")
        
        service.start()
    except Exception as e:
        log.error(f"Service failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
