import os
import time
from gpiozero import LED
from core.config import Config
from core.mpd_client import MPDClient
from utils.storage import find_usb_drive, copy_directory

class USBCopyService:
    def __init__(self):
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

    def _blink_error(self):
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
                print("ERROR: No track currently playing")
                raise Exception("No track currently playing")
            
            print("\n=== USB DRIVE DETECTION ===")
            usb_path = find_usb_drive(self.min_usb_size)
            if not usb_path:
                print("ERROR: No compatible USB device found")
                raise Exception("No compatible USB device found")
            
            print("\n=== PATH ANALYSIS ===")
            file_path = song['file']
            current_file = os.path.basename(file_path)
            print(f"  Current file: {current_file}")
            print(f"  File path: {file_path}")
            
            print("\n=== PATH VALIDATION ===")
            path_parts = file_path.split('/')
            if len(path_parts) >= self.path_structure['min_depth']:
                source_dir = os.path.join(
                    self.path_structure['music_root'],
                    os.path.dirname(file_path)
                )
                print(f"  Source directory: {source_dir}")
                
                album_path = '/'.join(path_parts[:self.path_structure['album_level']])
                dest_dir = os.path.join(usb_path, album_path)
                print(f"  Destination directory: {dest_dir}")
                
                print("\n=== COPY PROCESS ===")
                print("  Status: Starting copy...")
                files_copied, total_size = copy_directory(source_dir, dest_dir)
                print("\n=== COPY COMPLETE ===")
                print(f"  Files copied: {files_copied}")
                print(f"  Total size: {total_size/1024/1024:.2f} MB")
                print(f"  Album path: {album_path}")
                
                print("\n=== DESTINATION CONTENTS ===")
                for root, dirs, files in os.walk(dest_dir):
                    rel_path = os.path.relpath(root, dest_dir)
                    if rel_path == '.':
                        print("  Root directory contents:")
                    else:
                        print(f"  Directory: {rel_path}")
                    
                    if files:
                        for f in files:
                            file_path = os.path.join(root, f)
                            size = os.path.getsize(file_path)
                            print(f"    - {f} ({size/1024/1024:.2f} MB)")
            
            else:
                print("ERROR: Invalid directory structure")
                raise Exception("Invalid directory structure")
            
        except OSError as e:
            if e.errno == 28:
                print("ERROR: USB drive is full")
                raise Exception("USB drive is full")
            raise
            
        except Exception as e:
            print(f"ERROR: Copy failed: {str(e)}")
            self._blink_error()
            raise e
        
        finally:
            self.copy_led.off()
    
