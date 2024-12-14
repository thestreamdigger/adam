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
        copy_led_pin = self.config.get('gpio.leds.copy')
        self.copy_led = LED(copy_led_pin)
        self.copy_led.off()
        
        copy_config = self.config.get('copy', {})
        self.destination_skip_folders = copy_config.get('destination_skip_folders', [])
        self.path_structure = copy_config.get('path_structure', {
            'min_depth': 4,
            'artist_level': 2,
            'album_level': 3,
            'music_root': '/var/lib/mpd/music',
            'preserve_levels': [2, 3]
        })
        self.min_usb_size = copy_config.get('min_usb_size_gb', 4)
        log.ok("USB copy service initialized")

    def _blink_error(self):
        log.debug("Blinking error LED")
        for _ in range(3):
            self.copy_led.on()
            time.sleep(0.2)
            self.copy_led.off()
            time.sleep(0.2)

    def copy_current_track(self):
        try:
            self.copy_led.on()
            
            song = self.mpd.get_current_song()
            if not song or 'file' not in song:
                log.error("No track currently playing")
                raise Exception("No track currently playing")
            
            log.info("=== USB DRIVE DETECTION ===")
            usb_path = find_usb_drive(self.min_usb_size)
            if not usb_path:
                log.error("No compatible USB device found")
                raise Exception("No compatible USB device found")
            
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
                    
                    dest_dir = os.path.join(usb_path, preserved_path)
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
            log.error(f"Copy failed: {str(e)}")
            self._blink_error()
            raise e
        
        finally:
            self.copy_led.off()

