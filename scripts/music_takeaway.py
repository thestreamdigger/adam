#!/usr/bin/env python3
import os
import sys
import socket

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.service.usb_copy_service import USBCopyService
from src.utils.logger import Logger

log = Logger()

def main():
    try:
        log.info("Starting USB copy operation")
        copy_service = USBCopyService()
        log.wait("Copying current track")
        copy_service.copy_current_track()
        log.ok("Copy operation completed")
        
    except Exception as e:
        log.error(f"Error during copy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 