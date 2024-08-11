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

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LEDS, GPIO.OUT, initial=GPIO.LOW)

def clear_gpio():
    GPIO.cleanup(LEDS)

def run_leds(stop_event):
    current_led = 0
    while not stop_event.is_set():
        GPIO.output(LEDS[current_led], GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LEDS[current_led], GPIO.LOW)
        current_led = (current_led + 1) % len(LEDS)

def blink_leds(blink_count=3, blink_duration=0.5):
    for _ in range(blink_count):
        for led in LEDS:
            GPIO.output(led, GPIO.HIGH)
        time.sleep(blink_duration)
        for led in LEDS:
            GPIO.output(led, GPIO.LOW)
        time.sleep(blink_duration)

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
        for file in os.listdir(album_dir):
            src = os.path.join(album_dir, file)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(dest_dir, file))
        return True
    except Exception as e:
        print(f"Error copying files to USB: {e}")
        return False

def stop_service():
    os.system("pkill -f control.py")
    os.system("sudo systemctl stop control.service")

def start_service():
    os.system("sudo systemctl start control.service")

def main():
    stop_service()
    setup_gpio()
    stop_event = threading.Event()
    leds_thread = None
    client = MPDClient()
    try:
        client.connect(MPD_HOST, MPD_PORT)
        song = client.currentsong()
        song_path = song.get('file', '') if song else ''
        if song_path and not song_path.startswith('/mnt/'):
            song_path = '/mnt/' + song_path.strip('/')
        if not os.path.exists(song_path):
            blink_leds()
        else:
            usb_drive = find_usb_drive()
            if usb_drive and not usb_drive.startswith("Error"):
                leds_thread = threading.Thread(target=run_leds, args=(stop_event,))
                leds_thread.start()
                if not copy_to_usb(song_path, usb_drive):
                    blink_leds()
                eject_usb(usb_drive)
                stop_event.set()
            else:
                blink_leds()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()
        client.disconnect()
        stop_event.set()
        if leds_thread:
            leds_thread.join()
        clear_gpio()
        start_service()

if __name__ == '__main__':
    main()
