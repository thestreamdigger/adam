import os
import time
from gpiozero import LED
from core.config import Config
from core.mpd_client import MPDClient
from utils.storage import find_usb_drive, copy_directory

class USBCopyService:
    """Service for handling USB copy operations with LED feedback"""
    def __init__(self):
        self.config = Config()
        self.mpd = MPDClient()
        copy_led_pin = self.config.get('gpio.leds.copy')
        self.copy_led = LED(copy_led_pin)
        self.copy_led.off()
        
        # Get copy configuration
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
        """Indicate error through LED"""
        for _ in range(3):
            self.copy_led.on()
            time.sleep(0.2)
            self.copy_led.off()
            time.sleep(0.2)

    def copy_current_track(self):
        """Copy current track to USB with LED feedback"""
        try:
            self.copy_led.on()
            
            # Get current song info
            song = self.mpd.get_current_song()
            if not song or 'file' not in song:
                raise Exception("No track currently playing")
                
            # Find USB drive
            print("\n=== USB DETECTION ===")
            print("Searching for USB drive...")
            usb_path = find_usb_drive(self.min_usb_size)
            if not usb_path:
                raise Exception("No compatible USB drive found")
            print(f"USB drive found: {usb_path}")
                
            # Get file path components
            print("\n=== PATH ANALYSIS ===")
            file_path = song['file']
            current_file = os.path.basename(file_path)
            directory_path = os.path.dirname(file_path)
            path_components = directory_path.split('/')
            
            print(f"Current file path: {file_path}")
            print(f"Current file name: {current_file}")
            print("\nDirectory structure by level:")
            for i, component in enumerate(path_components):
                print(f"Level {i}: {component}")
            
            print("\n=== CONFIGURATION ===")
            print(f"Minimum directory depth required: {self.path_structure['min_depth']}")
            print(f"Artist level: {self.path_structure['artist_level']}")
            print(f"Album level: {self.path_structure['album_level']}")
            print(f"Preserve levels: {self.path_structure['preserve_levels']}")
            
            # Validate path structure
            if len(path_components) >= self.path_structure['min_depth']:
                print("\n=== STRUCTURE VALIDATION ===")
                print(f"Directory depth: {len(path_components)} (Valid: >= {self.path_structure['min_depth']})")
                
                # Extract artist and album paths
                artist_path = path_components[self.path_structure['artist_level']]
                album_path = path_components[self.path_structure['album_level']]
                print(f"Artist (Level {self.path_structure['artist_level']}): {artist_path}")
                print(f"Album (Level {self.path_structure['album_level']}): {album_path}")
                
                # Build source and destination paths
                print("\n=== SOURCE PATH CONSTRUCTION ===")
                source_components = path_components[:self.path_structure['album_level'] + 1]
                print("Source components:")
                for i, comp in enumerate(source_components):
                    print(f"Level {i}: {comp}")
                
                source_dir = os.path.join(
                    self.path_structure['music_root'],
                    *source_components
                )
                print(f"Final source directory: {source_dir}")
                
                # Build destination path preserving specified levels
                print("\n=== DESTINATION PATH CONSTRUCTION ===")
                print("Processing preserve levels:", self.path_structure['preserve_levels'])
                dest_components = []
                for level in self.path_structure['preserve_levels']:
                    if level < len(path_components):
                        component = path_components[level]
                        print(f"Checking level {level}: {component}")
                        if component != current_file:
                            print(f"  - Added to destination path")
                            dest_components.append(component)
                        else:
                            print(f"  - Skipped (current file)")
                    else:
                        print(f"  - Level {level} not available in path")
                
                print("\nDestination components:")
                for i, comp in enumerate(dest_components):
                    print(f"Level {i}: {comp}")
                
                dest_dir = os.path.join(usb_path, *dest_components)
                print(f"Final destination directory: {dest_dir}")
                
                # Copy files
                try:
                    print("\n=== COPY PROCESS ===")
                    print("Starting copy...")
                    files_copied, total_size = copy_directory(source_dir, dest_dir)
                    print(f"\nCopy completed!")
                    print(f"Files copied: {files_copied}")
                    print(f"Total size: {total_size/1024/1024:.2f} MB")
                    print(f"Copied album directory: {album_path}")
                    
                    # List contents of destination directory
                    print("\n=== DESTINATION CONTENTS ===")
                    first = True
                    for root, dirs, files in os.walk(dest_dir):
                        rel_path = os.path.relpath(root, dest_dir)
                        
                        if rel_path == '.':
                            print("\nRoot directory contents:")
                        else:
                            print(f"\n{rel_path} contents:")
                        
                        if files:
                            for f in files:
                                file_path = os.path.join(root, f)
                                size = os.path.getsize(file_path)
                                print(f"  - {f} ({size/1024/1024:.2f} MB)")
                
                except OSError as e:
                    if e.errno == 28:  # No space left on device
                        raise Exception("USB drive is full")
                    raise
                    
            else:
                raise Exception("Invalid directory structure")
                
        except Exception as e:
            print(f"\n=== ERROR ===")
            print(f"Error during copy: {str(e)}")
            self._blink_error()
            raise e
            
        finally:
            self.copy_led.off()
    
