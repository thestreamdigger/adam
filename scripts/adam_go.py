#!/usr/bin/env python3
import os
import sys

# Add src directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from service.usb_copy_service import USBCopyService

def main():
    try:
        copy_service = USBCopyService()
        copy_service.copy_current_track()
        
    except Exception as e:
        print(f"Error during copy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 