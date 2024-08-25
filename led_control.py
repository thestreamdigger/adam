import time
import RPi.GPIO as GPIO
from mpd import MPDClient
import subprocess
import signal

MPD_HOST = 'localhost'
MPD_PORT = 6600
LED_REPEAT = 17
LED_RANDOM = 27
LED_SINGLE = 22
LED_CONSUME = 10

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setup(LED_REPEAT, GPIO.OUT)
GPIO.setup(LED_RANDOM, GPIO.OUT)
GPIO.setup(LED_SINGLE, GPIO.OUT)
GPIO.setup(LED_CONSUME, GPIO.OUT)

client = MPDClient()

def check_mpd(host, port):
    while True:
        result = subprocess.run(["nc", "-z", host, str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return
        else:
            time.sleep(5)

def connect_mpd():
    try:
        client.connect(MPD_HOST, MPD_PORT)
        return True
    except ConnectionRefusedError:
        return False

def set_led_state(pin, state):
    current_state = GPIO.input(pin)
    if current_state != state:
        GPIO.output(pin, state)

def handle_shutdown(signum, frame):
    GPIO.cleanup()
    if connected:
        client.close()
        client.disconnect()
    exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGUSR1, handle_shutdown)

check_mpd(MPD_HOST, MPD_PORT)
connected = connect_mpd()
last_state = {'repeat': '0', 'random': '0', 'single': '0', 'consume': '0'}

try:
    while connected:
        state = client.status()
        set_led_state(LED_REPEAT, state['repeat'] == '1')
        set_led_state(LED_RANDOM, state['random'] == '1')
        set_led_state(LED_SINGLE, state['single'] == '1')
        set_led_state(LED_CONSUME, state['consume'] == '1')
        last_state = state
        time.sleep(1)
except Exception as e:
    pass
finally:
    GPIO.cleanup()
    if connected:
        client.close()
        client.disconnect()
