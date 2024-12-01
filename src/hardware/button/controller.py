import os
import time
import subprocess
from gpiozero import Button
from core.config import Config

class ButtonController:
    """Controls the physical button with real-time config updates"""
    def __init__(self):
        self.config = Config()
        self._setup_button()
        self.last_command_time = 0
        self.press_start_time = None  # To track press duration
        self.config.add_observer(self._setup_button)

    def _setup_button(self):
        """Setup button with current config"""
        button_pin = self.config.get('gpio.button')
        self.long_press_time = self.config.get('timing.long_press_time', 2)
        
        self.button = Button(
            button_pin,
            pull_up=True
        )
        
        self.button.when_pressed = self._start_press
        self.button.when_released = self._handle_release

        self.command_cooldown = self.config.get('timing.command_cooldown', 1)

    def _start_press(self):
        """Record the start time of the button press"""
        self.press_start_time = time.time()

    def _handle_release(self):
        """Handle action based on press duration upon release"""
        if self.press_start_time is None:
            return  # Ensure press start time is valid

        press_duration = time.time() - self.press_start_time
        self.press_start_time = None  # Reset for next press
        
        current_time = time.time()
        if (current_time - self.last_command_time) < self.command_cooldown:
            return  # Ignore if within cooldown
        
        # Determine whether it's a long or short press
        if press_duration >= self.long_press_time:
            self._execute_long_press()
        else:
            self._execute_short_press()

    def _execute_short_press(self):
        """Execute the action for a short press"""
        self.last_command_time = time.time()
        script_path = self.config.get('paths.roulette')
        
        if not script_path:
            print("ERROR: Script configuration not found")
            return
        
        if not os.path.exists(script_path):
            print("ERROR: Script not found")
            return
        
        try:
            subprocess.run(['sudo', script_path], check=True)
        except subprocess.CalledProcessError:
            print("ERROR: Script execution failed")

    def _execute_long_press(self):
        """Execute the action for a long press"""
        self.last_command_time = time.time()
        script_path = self.config.get('paths.shutdown')
        
        if not script_path:
            print("ERROR: Script configuration not found")
            return
        
        if not os.path.exists(script_path):
            print("ERROR: Script not found")
            return
        
        try:
            subprocess.run(['sudo', script_path], check=True)
        except subprocess.CalledProcessError:
            print("ERROR: Script execution failed")

    def cleanup(self):
        """Cleanup resources"""
        self.config.remove_observer(self._setup_button)
