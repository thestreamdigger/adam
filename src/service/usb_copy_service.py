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
                print("[ERROR]  No track currently playing")
                raise Exception("No track currently playing")
            
            # Primeiro detectamos o USB
            usb_path = find_usb_drive(self.min_usb_size)
            if not usb_path:
                print("[ERROR]  No compatible USB device found")
                raise Exception("No compatible USB device found")
            
            # Depois analisamos o caminho
            print("[INFO]   === PATH ANALYSIS ===")
            file_path = song['file']
            current_file = os.path.basename(file_path)
            print(f"[DEBUG]  Current file: {current_file}")
            print(f"[DEBUG]  File path: {file_path}")
            
            print("[INFO]   === PATH VALIDATION ===")
            path_parts = file_path.split('/')
            if len(path_parts) >= self.path_structure['min_depth']:
                # Source: mantemos o caminho original completo
                source_dir = os.path.join(
                    self.path_structure['music_root'],
                    os.path.dirname(file_path)
                )
                print(f"[DEBUG]  Source directory: {source_dir}")
                
                # Destination: aplicamos os filtros
                dest_parts = path_parts.copy()
                print(f"[DEBUG]  Original path parts: {dest_parts}")
                
                dest_parts = [part for part in dest_parts if part not in self.destination_skip_folders]
                print(f"[DEBUG]  After skip folders: {dest_parts}")
                
                if len(dest_parts) >= 2:
                    artist = dest_parts[0]
                    album = dest_parts[1]
                    
                    preserved_path = os.path.join(artist, album)
                    print(f"[DEBUG]  Preserved path: {preserved_path}")
                    
                    dest_dir = os.path.join(usb_path, preserved_path)
                    print(f"[DEBUG]  Destination directory: {dest_dir}")
                    
                    print("[WAIT]   Starting copy process...")
                    files_copied, total_size = copy_directory(source_dir, dest_dir)
                    print("[OK]     Copy process initiated")
                    print("\n[INFO]   === COPY COMPLETE ===")
                    print(f"[OK]     Files copied: {files_copied}")
                    print(f"[INFO]   Total size: {total_size/1024/1024:.2f} MB")
                    print(f"[INFO]   Album path: {preserved_path}")
                
            else:
                print("[ERROR]  Invalid directory structure")
                raise Exception("Invalid directory structure")
            
        except OSError as e:
            if e.errno == 28:
                print("[ERROR]  USB drive is full")
                raise Exception("USB drive is full")
            raise
            
        except Exception as e:
            print(f"[ERROR]  Copy failed: {str(e)}")
            self._blink_error()
            raise e
        
        finally:
            self.copy_led.off()

