import os
import time
from gpiozero import LED
from src.core.config import Config
from src.core.mpd_client import MPDClient
from src.utils.storage import find_usb_drive, copy_directory
from src.utils.logger import Logger

log = Logger()

class USBCopyService:
    def __init__(self):
        log.debug("Initializing USB copy service")
        self.config = Config()
        self.mpd = MPDClient()
        
        copy_config = self.config.get('copy', {})
        self.min_usb_size = copy_config.get('min_usb_size_gb', 4)
        self.path_structure = copy_config.get('path_structure', {})
        self.destination_skip_folders = copy_config.get('destination_skip_folders', [])
        
        copy_led_pin = copy_config.get('led')
        if not copy_led_pin:
            log.warning("Copy LED pin not configured")
        self.copy_led = LED(copy_led_pin) if copy_led_pin else None
        if self.copy_led:
            self.copy_led.off()
            log.debug(f"Copy LED initialized on GPIO {copy_led_pin}")

    def copy_current_track(self):
        try:
            log.wait("Attempting to connect to MPD...")
            self.mpd.connect()
            log.ok("Connected to MPD at localhost:6600")
            
            song = self.mpd.get_current_song()
            if not song or 'file' not in song:
                raise Exception("No track currently playing")
            
            log.info("=== USB DRIVE DETECTION ===")
            usb_info = find_usb_drive(self.min_usb_size)
            if not usb_info:
                raise Exception("No suitable USB drive found")
            
            if self.copy_led:
                self.copy_led.on()
                log.debug("Copy LED turned on - starting copy process")
            
            log.info("=== PATH ANALYSIS ===")
            file_path = song['file']
            current_file = os.path.basename(file_path)
            log.debug(f"Current file: {current_file}")
            log.debug(f"File path: {file_path}")
            
            log.info("=== PATH VALIDATION ===")
            path_parts = file_path.split('/')
            if len(path_parts) >= self.path_structure['min_depth']:
                source_dir = os.path.join(
                    self.path_structure['music_root'],
                    os.path.dirname(file_path)
                )
                log.debug(f"Source directory: {source_dir}")
                
                dest_parts = path_parts.copy()
                log.debug(f"Original path parts: {dest_parts}")
                
                dest_parts = [part for part in dest_parts if part not in self.destination_skip_folders]
                log.debug(f"After skip folders: {dest_parts}")
                
                if len(dest_parts) >= 2:
                    artist = dest_parts[0]
                    album = dest_parts[1]
                    
                    preserved_path = os.path.join(artist, album)
                    log.debug(f"Preserved path: {preserved_path}")
                    
                    dest_dir = os.path.join(usb_info, preserved_path)
                    log.debug(f"Destination directory: {dest_dir}")
                    
                    log.wait("Starting copy process...")
                    files_copied, total_size = copy_directory(source_dir, dest_dir)
                    log.ok("Copy process completed")
                    
                    log.info("=== COPY COMPLETE ===")
                    log.info(f"Files copied: {files_copied}")
                    log.info(f"Total size: {total_size/1024/1024:.2f} MB")
                    log.info(f"Album path: {preserved_path}")
                
            else:
                log.error("Invalid directory structure")
                raise Exception("Invalid directory structure")
            
        except OSError as e:
            if e.errno == 28:
                log.error("USB drive is full")
                raise Exception("USB drive is full")
            raise
            
        except Exception as e:
            if self.copy_led:
                log.debug("Error indication: blinking copy LED")
                for _ in range(3):
                    self.copy_led.on()
                    time.sleep(0.2)
                    self.copy_led.off()
                    time.sleep(0.2)
            raise e
        
        finally:
            if self.copy_led:
                self.copy_led.off()
                log.debug("Copy LED turned off")

