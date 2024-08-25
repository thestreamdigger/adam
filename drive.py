import os
import time
import shutil
import psutil
import threading
import RPi.GPIO as GPIO
from mpd import MPDClient

MPD_HOST = 'localhost'
MPD_PORT = 6600
LED_REPEAT = 17
LED_RANDOM = 27
LED_SINGLE = 22
LED_CONSUME = 10
LEDS = [LED_REPEAT, LED_RANDOM, LED_SINGLE, LED_CONSUME]
MOUNT_POINT = '/mnt/'

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LEDS, GPIO.OUT, initial=GPIO.LOW)

def clear_gpio():
    GPIO.cleanup(LEDS)

def blink_pattern(pattern, duration=0.2):
    for step in pattern:
        for i, state in enumerate(step):
            GPIO.output(LEDS[i], state)
        time.sleep(duration)
    for led in LEDS:
        GPIO.output(led, GPIO.LOW)

PATTERNS = {
    'copying': [[1,0,1,0], [1,1,1,1], [0,1,0,1], [0,0,0,0]],
    'error': [[1,1,1,1], [0,0,0,0]] * 3
}

def indicate_state(state, duration=None):
    if state in PATTERNS:
        if state == 'copying' and duration:
            start_time = time.time()
            while time.time() - start_time < duration:
                blink_pattern(PATTERNS[state])
        else:
            blink_pattern(PATTERNS[state])
    else:
        print(f"Pattern not defined for state: {state}")

def eject_usb(drive):
    try:
        os.system(f'sudo eject {drive}')
    except Exception as e:
        print(f"Failed to eject USB drive: {e}")

def find_usb_drive():
    try:
        mounted_drives = [device.mountpoint for device in psutil.disk_partitions() if device.mountpoint.startswith('/media/')]
        if len(mounted_drives) == 1:
            return mounted_drives[0]
        elif len(mounted_drives) > 1:
            return "Error: Multiple USB drives detected."
        else:
            return None
    except Exception as e:
        print(f"Error finding USB drives: {e}")
        return None

def copy_to_usb(full_path, usb_drive):
    try:
        if not os.path.exists(full_path):
            print(f"Directory not found: {full_path}")
            return False
        path_components = os.path.normpath(full_path).split(os.sep)
        artist_name = path_components[-3] if len(path_components) > 3 else 'UnknownArtist'
        album_name = path_components[-2] if len(path_components) > 3 else 'UnknownAlbum'
        dest_dir = os.path.join(usb_drive, artist_name, album_name)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        album_dir = os.path.join('/', *path_components[:-1])
        if not os.path.exists(album_dir):
            print(f"Album directory not found: {album_dir}")
            return False
        
        copying_event = threading.Event()
        copying_thread = threading.Thread(target=indicate_state, args=('copying',), kwargs={'duration': float('inf')})
        copying_thread.start()
        
        for file in os.listdir(album_dir):
            src = os.path.join(album_dir, file)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(dest_dir, file))
        
        copying_event.set()
        copying_thread.join(timeout=0.1)
        return True
    except Exception as e:
        print(f"Error copying files to USB: {e}")
        return False

def stop_service():
    os.system("pkill -f control.py")
    os.system("sudo systemctl stop led_control.service")

def start_service():
    os.system("sudo systemctl start led_control.service")

def main():
    stop_service()
    setup_gpio()
    client = MPDClient()
    try:
        client.connect(MPD_HOST, MPD_PORT)
        song = client.currentsong()
        song_path = song.get('file', '') if song else ''
        if song_path and not song_path.startswith(MOUNT_POINT):
            song_path = os.path.join(MOUNT_POINT, song_path.strip('/'))
        if not os.path.exists(song_path):
            indicate_state('error')
        else:
            usb_drive = find_usb_drive()
            if usb_drive and not usb_drive.startswith("Error"):
                if copy_to_usb(song_path, usb_drive):
                    eject_usb(usb_drive)
                else:
                    indicate_state('error')
            else:
                print("No USB drive found or multiple drives detected.")
                indicate_state('error')
    except Exception as e:
        print(f"An error occurred: {e}")
        indicate_state('error')
    finally:
        client.close()
        client.disconnect()
        clear_gpio()
        start_service()

if __name__ == '__main__':
    main()