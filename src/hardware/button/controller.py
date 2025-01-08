import os
import time
import subprocess
from gpiozero import Button
from src.core.config import Config
from src.utils.logger import Logger

log = Logger()

class ButtonController:
    def __init__(self):
        log.debug("Initializing button controller")
        self.config = Config()
        self.button = None
        self._setup_button()
        self.last_command_time = 0
        self.press_start_time = None
        
        log.info("Loading button timings...")
        self.command_cooldown = self.config.get('timing.command_cooldown', 0.5)
        self.long_press_time = self.config.get('timing.long_press_time', 2)
        
        log.info("Registering button handlers...")
        self._setup_button()
        
        log.ok("Button controller initialized")

    def _setup_button(self):
        log.info("Setting up button hardware...")
        try:
            if self.button:
                self.button.close()
                self.button = None

            button_pin = self.config.get('gpio.button')
            if not button_pin:
                log.error("Button pin not configured")
                return

            self.button = Button(
                button_pin,
                pull_up=True,
                bounce_time=0.1
            )
            
            self.button.when_pressed = self._on_press
            self.button.when_released = self._on_release
            log.ok("Button setup complete")
            
        except Exception as e:
            log.error(f"Failed to setup button: {e}")

    def _on_press(self):
        self.press_start_time = time.time()

    def _on_release(self):
        if self.press_start_time is None:
            return

        press_duration = time.time() - self.press_start_time
        self.press_start_time = None
        
        current_time = time.time()
        if (current_time - self.last_command_time) < self.command_cooldown:
            return
        
        if press_duration >= self.long_press_time:
            self._execute_long_press()
        else:
            self._execute_short_press()

    def _execute_short_press(self):
        log.debug("Button: Short press detected")
        self.last_command_time = time.time()
        script_path = self.config.get('paths.roulette')
        
        if not script_path:
            log.error("Script configuration not found")
            return
        
        if not os.path.exists(script_path):
            log.error(f"Script not found: {script_path} (roulette)")
            return
        
        try:
            log.wait("Executing roulette script")
            subprocess.run(['sudo', script_path], check=True)
            log.ok("Roulette script executed")
        except subprocess.CalledProcessError:
            log.error("Script execution failed")

    def _execute_long_press(self):
        log.debug("Button: Long press detected")
        self.last_command_time = time.time()
        script_path = self.config.get('paths.shutdown')
        
        if not script_path:
            log.error("Script configuration not found")
            return
        
        if not os.path.exists(script_path):
            log.error(f"Script not found: {script_path} (shutdown)")
            return
        
        try:
            log.wait("Executing shutdown script")
            subprocess.run(['sudo', script_path], check=True)
            log.ok("Shutdown script executed")
        except subprocess.CalledProcessError:
            log.error("Script execution failed")

    def cleanup(self):
        log.debug("Cleaning up button controller")
        if self.button:
            self.button.close()
            self.button = None
        log.ok("Button controller cleanup complete")
