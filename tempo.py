import os
import time
import tm1637
import subprocess
import signal
from mpd import MPDClient, CommandError, ConnectionError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import RPi.GPIO as GPIO

# Constants
SEGMENT_MAP = {
    '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F, '4': 0x66, '5': 0x6D, 
    '6': 0x7D, '7': 0x07, '8': 0x7F, '9': 0x6F, '-': 0x40, ' ': 0x00
}

CONFIG_FILE = 'tempo.cfg'
CLK_GPIO = 15
DIO_GPIO = 14
COLON_MASK = 0b10000000
LED_ERROR_PIN = 12

# Configuration Handler
class ConfigHandler(FileSystemEventHandler):
    def __init__(self, filename):
        self.filename = filename
        self.load()
        self.observer = Observer()
        self.observer.schedule(self, path=os.path.dirname(os.path.abspath(self.filename)), recursive=False)
        self.observer.start()
        self.modified = False

    def load(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as file:
                file.write("BRIGHTNESS = 2\n")
        with open(self.filename, 'r') as file:
            lines = file.readlines()
        self.mpd_host = self.get_value("MPD_HOST", lines, default="localhost")
        self.mpd_port = int(self.get_value("MPD_PORT", lines, default="6600"))
        self.display_mode = self.get_value("DISPLAY", lines, default="elapsed")
        self.brightness = int(self.get_value("BRIGHTNESS", lines, default="2"))
        self.track_display_duration = int(self.get_value("TRACK_DISPLAY_DURATION", lines, default="1"))
        self.volume_display_duration = int(self.get_value("VOLUME_DISPLAY_DURATION", lines, default="3"))
        self.update_interval = float(self.get_value("UPDATE_INTERVAL", lines, default="1"))
        self.volume_update_interval = float(self.get_value("VOLUME_UPDATE_INTERVAL", lines, default="0.1"))
        self.enable_error_led = self.get_value("ENABLE_ERROR_LED", lines, default="False").lower() in ('true', '1', 't')
        self.modified = True

    def on_modified(self, event):
        if event.src_path == os.path.abspath(self.filename):
            self.load()

    @staticmethod
    def get_value(key, lines, default=None):
        for line in lines:
            parts = line.split('=')
            if parts[0].strip().upper() == key:
                return parts[1].strip()
        return default

    def stop(self):
        self.observer.stop()
        self.observer.join()

# GPIO Setup
def setup_gpio(enable_error_led):
    GPIO.setmode(GPIO.BCM)
    if enable_error_led:
        GPIO.setup(LED_ERROR_PIN, GPIO.OUT)
        GPIO.output(LED_ERROR_PIN, GPIO.LOW)

# MPD Client Functions
def check_mpd_availability(host, port):
    while True:
        result = subprocess.run(["nc", "-z", host, str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return
        else:
            time.sleep(5)

def connect_to_mpd(host, port):
    client = MPDClient()
    check_mpd_availability(host, port)
    while True:
        try:
            client.connect(host, port)
            return client
        except ConnectionError:
            time.sleep(5)

def ensure_mpd_connection(client, host, port, display, config):
    if client is None:
        client = connect_to_mpd(host, port)
        if client is None:
            display_message(display, ['-', '-', '-', '-'])
            time.sleep(5)
            return ensure_mpd_connection(None, host, port, display, config)
    else:
        try:
            client.ping()
        except (ConnectionError, CommandError):
            handle_connection_error(display)
            return ensure_mpd_connection(None, host, port, display, config)
    return client

def get_mpd_status(client, display):
    try:
        status = client.status()
        player_state = status.get('state', 'N/A')
        current_volume = status.get('volume', 'N/A')
        elapsed_time = status.get('elapsed', 'N/A')
        total_time = status.get('duration', 'N/A')
        if 'error' in status:
            handle_connection_error(display)
        return player_state, current_volume, elapsed_time, total_time
    except CommandError:
        handle_connection_error(display)
        return 'N/A', 'N/A', 'N/A', 'N/A'

# Display Functions
def display_message(display, text, colon_on=False):
    segment_bytes = [SEGMENT_MAP.get(digit, 0x00) for digit in text]
    if colon_on:
        segment_bytes[1] |= COLON_MASK
    display.write(segment_bytes)

def clear_display(display):
    display.write([0x00, 0x00, 0x00, 0x00])

def blink_error_display(display):
    for _ in range(5):
        display_message(display, ['-', '-', '-', '-'])
        time.sleep(0.2)
        clear_display(display)
        time.sleep(0.2)

def handle_connection_error(display):
    blink_error_display(display)

def blink_error_led(config):
    if config.enable_error_led:
        for _ in range(5):
            GPIO.output(LED_ERROR_PIN, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(LED_ERROR_PIN, GPIO.LOW)
            time.sleep(0.5)

def get_display_time(display_mode, elapsed_time, total_time):
    try:
        if display_mode == "remaining" and total_time != 'N/A':
            time_value = float(total_time) - float(elapsed_time)
        else:
            time_value = float(elapsed_time)
        minutes, seconds = divmod(int(time_value), 60)
        return f"{minutes:02d}{seconds:02d}"
    except ValueError:
        return "0000"

# Signal Handling
def handle_shutdown(signum, frame):
    display = tm1637.TM1637(clk=CLK_GPIO, dio=DIO_GPIO)
    clear_display(display)
    display.brightness(0)
    GPIO.cleanup()
    exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGUSR1, handle_shutdown)

# Main Function
def main():
    config = ConfigHandler(CONFIG_FILE)
    setup_gpio(config.enable_error_led)
    display = tm1637.TM1637(clk=CLK_GPIO, dio=DIO_GPIO)
    display.brightness(config.brightness)
    display_message(display, ['-', '-', '-', '-'])
    client = ensure_mpd_connection(None, config.mpd_host, config.mpd_port, display, config)
    colon_on = False
    last_volume = None
    volume_display_until = 0
    display_volume = False
    last_track_number = None
    display_index = 0

    update_interval = config.update_interval
    volume_update_interval = config.volume_update_interval

    try:
        while True:
            start_time = time.monotonic()

            # Reload configuration if modified
            if config.modified:
                display.brightness(config.brightness)
                config.modified = False

            client = ensure_mpd_connection(client, config.mpd_host, config.mpd_port, display, config)
            player_state, current_volume, elapsed_time, total_time = get_mpd_status(client, display)
            current_playlist = client.playlistinfo()
            current_song = client.currentsong()
            track_number = current_song.get('track', None)

            if last_volume != current_volume:
                last_volume = current_volume
                volume_display_until = time.monotonic() + config.volume_display_duration
                display_volume = True

            if time.monotonic() < volume_display_until and display_volume:
                display_volume_message(display, current_volume, volume_update_interval)
                continue

            if player_state == "play":
                handle_play_mode(display, config, client, elapsed_time, total_time, track_number, last_track_number, colon_on)
                colon_on = not colon_on
                last_track_number = track_number

            elif player_state == "pause":
                handle_pause_mode(display, config, elapsed_time, total_time, colon_on)
                colon_on = not colon_on

            elif player_state == "stop":
                handle_stop_mode(display, current_playlist, display_index)
                display_index = (display_index + 1) % 3

            elapsed_iteration = time.monotonic() - start_time
            sleep_time = max(update_interval - elapsed_iteration, 0)
            time.sleep(sleep_time)
    finally:
        config.stop()
        cleanup()

def display_volume_message(display, current_volume, volume_update_interval):
    padded_volume = f"{int(current_volume):>4}".replace(" ", "-")
    display_message(display, padded_volume)
    time.sleep(volume_update_interval)

def handle_play_mode(display, config, client, elapsed_time, total_time, track_number, last_track_number, colon_on):
    display_index = 0
    if track_number != last_track_number:
        if track_number and track_number.split('/')[0].isdigit():
            display_track_number = f"-{int(track_number.split('/')[0]):02d}-"
            display_message(display, display_track_number)
            time.sleep(config.track_display_duration)
    display_time = get_display_time(config.display_mode, elapsed_time, total_time)
    display_message(display, display_time, colon_on)

def handle_pause_mode(display, config, elapsed_time, total_time, colon_on):
    display_index = 0
    display_time = get_display_time(config.display_mode, elapsed_time, total_time)
    if colon_on:
        display_message(display, display_time, True)
    else:
        clear_display(display)
    time.sleep(config.update_interval)

def handle_stop_mode(display, current_playlist, display_index):
    if not current_playlist:
        display_message(display, ['-', '-', '-', '-'])
        time.sleep(3)
    else:
        total_tracks = len(current_playlist)
        total_duration = sum(float(track['duration']) if 'duration' in track else 0 for track in current_playlist)
        total_minutes, total_seconds = divmod(int(total_duration), 60)
        if display_index == 0:
            display_message(display, ['-', '-', '-', '-'])
        elif display_index == 1:
            display_track_number = f"{total_tracks:02d}--"
            display_message(display, display_track_number)
        elif display_index == 2:
            display_duration = f"{total_minutes:02d}{total_seconds:02d}"
            display_message(display, display_duration, True)
        time.sleep(2)

def cleanup():
    GPIO.cleanup()

if __name__ == '__main__':
    main()
