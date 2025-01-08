from gpiozero import PWMLED
from gpiozero.pins.lgpio import LGPIOFactory
from src.core.config import Config
from src.utils.logger import Logger

log = Logger()

class LEDController:
    def __init__(self):
        log.debug("Initializing LED controller")
        self.config = Config()
        
        led_config = self.config.get('gpio.leds', {})
        pwm_config = led_config.get('pwm', {})
        self.pwm_frequency = pwm_config.get('frequency', 1000)
        
        self._brightness_cache = None
        
        pin_factory = LGPIOFactory()
        
        self.leds = {
            'repeat': {'led': PWMLED(led_config['repeat'], 
                                   frequency=self.pwm_frequency,
                                   pin_factory=pin_factory), 
                      'state': False},
            'random': {'led': PWMLED(led_config['random'], 
                                   frequency=self.pwm_frequency,
                                   pin_factory=pin_factory), 
                      'state': False},
            'single': {'led': PWMLED(led_config['single'], 
                                   frequency=self.pwm_frequency,
                                   pin_factory=pin_factory), 
                      'state': False},
            'consume': {'led': PWMLED(led_config['consume'], 
                                    frequency=self.pwm_frequency,
                                    pin_factory=pin_factory), 
                      'state': False}
        }
        
        log.info("Setting up LEDs...")
        self._setup_leds()
        log.ok("LED controller initialized")
        self._last_status = {}

    def _setup_leds(self):
        try:
            display_level = self.config.get('display.brightness', 0)
            display_levels = self.config.get('display.brightness_levels.display', [0, 2, 7])
            led_levels = self.config.get('display.brightness_levels.led', [5, 25, 100])
            
            index = display_levels.index(display_level)
            brightness = led_levels[index] / 100.0
            
            for led_info in self.leds.values():
                if led_info['state']:
                    led_info['led'].value = brightness
                    
            log.debug(f"LED brightness set to {brightness*100}%")
            
        except Exception as e:
            log.error(f"LED setup failed: {e}")

    def update_from_mpd_status(self, status):
        if not status:
            return
            
        state_map = {
            'repeat': status.get('repeat', '0') == '1',
            'random': status.get('random', '0') == '1',
            'single': status.get('single', '0') == '1',
            'consume': status.get('consume', '0') == '1'
        }
        
        if state_map != self._last_status:
            if self._brightness_cache is None:
                display_level = self.config.get('display.brightness', 0)
                display_levels = self.config.get('display.brightness_levels.display', [0, 2, 7])
                led_levels = self.config.get('display.brightness_levels.led', [5, 25, 100])
                index = display_levels.index(display_level)
                self._brightness_cache = led_levels[index] / 100.0
            
            for led_name, state in state_map.items():
                if state != self._last_status.get(led_name):
                    led_info = self.leds.get(led_name)
                    if led_info:
                        led_info['state'] = state
                        led_info['led'].value = self._brightness_cache if state else 0
                        
            self._last_status = state_map.copy()

    def all_off(self):
        log.debug("Turning off all LEDs")
        for led_info in self.leds.values():
            led_info['led'].value = 0
            led_info['state'] = False

    def cleanup(self):
        log.info("Shutting down LEDs...")
        self.all_off()
        for led_info in self.leds.values():
            led_info['led'].close()
        log.ok("LED controller shutdown complete")

    def invalidate_brightness_cache(self):
        self._brightness_cache = None
