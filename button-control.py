import os
import time
import subprocess
import RPi.GPIO as GPIO

BUTTON_PIN = 18
LONG_PRESS_TIME = 2
COMMAND_COOLDOWN = 1

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_command_time = time.time() - COMMAND_COOLDOWN

def button_pressed(pin):
    global last_command_time
    current_time = time.time()
    if GPIO.input(pin) == GPIO.LOW and (current_time - last_command_time >= COMMAND_COOLDOWN):
        press_time = current_time
        while GPIO.input(pin) == GPIO.LOW:
            if (current_time - press_time) > LONG_PRESS_TIME:
                script_path = '/home/pi/shutdown.sh'
                if os.path.exists(script_path):
                    subprocess.run(['sudo', script_path], check=True)
                last_command_time = current_time
                return
            current_time = time.time()
            time.sleep(0.1)
        script_path = '/home/pi/roulette.sh'
        if os.path.exists(script_path):
            subprocess.run(['sudo', script_path], check=True)
        last_command_time = current_time

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed, bouncetime=200)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
