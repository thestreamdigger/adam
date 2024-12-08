from gpiozero import LED
from core.config import Config

class LEDController:
    """Controls the status LEDs with real-time config updates"""
    def __init__(self):
        self.config = Config()
        self._setup_leds()
        self.config.add_observer(self._setup_leds)

    def _setup_leds(self):
        """Setup LED objects with current config"""
        print("[INFO]   Setting up LEDs...")
        led_pins = self.config.get('gpio.leds')
        self.leds = {
            'repeat': LED(led_pins['repeat']),
            'random': LED(led_pins['random']),
            'single': LED(led_pins['single']),
            'consume': LED(led_pins['consume'])
        }

    def update_from_mpd_status(self, status):
        """Update LEDs based on MPD status"""
        if status is None:
            self.all_off()
            return

        state_map = {
            'repeat': status.get('repeat', '0') == '1',
            'random': status.get('random', '0') == '1',
            'single': status.get('single', '0') == '1',
            'consume': status.get('consume', '0') == '1'
        }

        for led_name, state in state_map.items():
            if state:
                self.leds[led_name].on()
            else:
                self.leds[led_name].off()

    def all_off(self):
        """Turn off all LEDs"""
        for led in self.leds.values():
            led.off()

    def cleanup(self):
        """Cleanup resources"""
        print("[INFO]   Shutting down LEDs...")
        self.config.remove_observer(self._setup_leds)
        self.all_off()
