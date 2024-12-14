from gpiozero import LED
from src.core.config import Config
from src.utils.logger import Logger

log = Logger()

class LEDController:
    def __init__(self):
        log.debug("Initializing LED controller")
        self.config = Config()
        self._setup_leds()
        self.config.add_observer(self._setup_leds)
        log.ok("LED controller initialized")

    def _setup_leds(self):
        log.info("Setting up LEDs...")
        led_pins = self.config.get('gpio.leds')
        self.leds = {
            'repeat': LED(led_pins['repeat']),
            'random': LED(led_pins['random']),
            'single': LED(led_pins['single']),
            'consume': LED(led_pins['consume'])
        }
        log.ok("LEDs setup complete")

    def update_from_mpd_status(self, status):
        if status is None:
            log.debug("No MPD status, turning off all LEDs")
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
                log.debug(f"LED {led_name}: ON")
            else:
                self.leds[led_name].off()
                log.debug(f"LED {led_name}: OFF")

    def all_off(self):
        log.debug("Turning off all LEDs")
        for led in self.leds.values():
            led.off()

    def cleanup(self):
        log.info("Shutting down LEDs...")
        self.config.remove_observer(self._setup_leds)
        self.all_off()
        log.ok("LED controller shutdown complete")
