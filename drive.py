import os
import time
import shutil
import psutil
import threading
import subprocess
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
    'error': [[1,1,1,1], [0,0,0,0]] * 3,
    'no_space': [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]] * 2
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
        print(f"Successfully ejected {drive}")
    except Exception as e:
        print(f"Failed to eject USB drive: {e}")

def find_usb_drive():
    try:
        partitions = psutil.disk_partitions(all=True)
        usb_drives = []
        for p in partitions:
            if p.device.startswith(('/dev/sd', '/dev/usb', '/dev/disk')):
                result = subprocess.run(['lsblk', '-ndo', 'rm', p.device], capture_output=True, text=True)
                if result.stdout.strip() == '1':
                    try:
                        usage = psutil.disk_usage(p.mountpoint)
                        size_gb = usage.total / (1024 * 1024 * 1024)
                        if size_gb >= 4:
                            usb_drives.append((p.mountpoint, size_gb))
                    except PermissionError:
                        print(f"Unable to access {p.mountpoint} due to insufficient permissions.")
        
        if not usb_drives:
            print("No compatible USB drive found (4GB+ required).")
            return None
        elif len(usb_drives) == 1:
            print(f"USB drive detected: {usb_drives[0][0]} ({usb_drives[0][1]:.2f} GB)")
            return usb_drives[0][0]
        else:
            print("Multiple USB drives detected. Selecting the first compatible one.")
            selected_drive = usb_drives[0][0]
            print(f"Selected USB drive: {selected_drive} ({usb_drives[0][1]:.2f} GB)")
            return selected_drive
    except Exception as e:
        print(f"Error finding USB drives: {e}")
        return None

def get_directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def check_free_space(usb_drive, required_space):
    try:
        stats = shutil.disk_usage(usb_drive)
        return stats.free > required_space
    except Exception as e:
        print(f"Error checking free space: {e}")
        return False

def copy_to_usb(full_path, usb_drive):
    try:
        if not os.path.exists(full_path):
            print(f"Directory not found: {full_path}")
            return False
        
        path_components = os.path.normpath(full_path).split(os.sep)
        artist_name = path_components[-3] if len(path_components) > 3 else 'UnknownArtist'
        album_name = path_components[-2] if len(path_components) > 3 else 'UnknownAlbum'
        dest_dir = os.path.join(usb_drive, artist_name, album_name)
        
        album_dir = os.path.join('/', *path_components[:-1])
        if not os.path.exists(album_dir):
            print(f"Album directory not found: {album_dir}")
            return False
        
        required_space = get_directory_size(album_dir)
        if not check_free_space(usb_drive, required_space):
            print("Not enough space on USB drive")
            indicate_state('no_space')
            eject_usb(usb_drive)
            return False
        
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        
        copying_event = threading.Event()
        copying_thread = threading.Thread(target=indicate_state, args=('copying',), kwargs={'duration': float('inf')})
        copying_thread.start()
        
        for file in os.listdir(album_dir):
            src = os.path.join(album_dir, file)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(dest_dir, file))
        
        copying_event.set()
        copying_thread.join(timeout=0.1)
        print(f"Successfully copied album to {dest_dir}")
        return True
    except Exception as e:
        print(f"Error copying files to USB: {e}")
        return False

def check_service_status(service_name):
    result = subprocess.run(['systemctl', 'is-active', service_name], capture_output=True, text=True)
    return result.stdout.strip()

def stop_led_control():
    os.system("sudo systemctl stop led_control.service")

def start_led_control():
    os.system("sudo systemctl start led_control.service")

def main():
    led_control_active = check_service_status('led_control.service') == 'active'
    if led_control_active:
        stop_led_control()
    
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
            if usb_drive:
                if not copy_to_usb(song_path, usb_drive):
                    indicate_state('error')
            else:
                indicate_state('error')
    except Exception as e:
        print(f"An error occurred: {e}")
        indicate_state('error')
    finally:
        client.close()
        client.disconnect()
        clear_gpio()
        if led_control_active:
            start_led_control()

if __name__ == '__main__':
    main()

