from gpiozero import DigitalOutputDevice
import time
from src.core.config import Config
from src.utils.logger import Logger

log = Logger()

class TM1637:
    COMMAND1 = 0x40
    COMMAND2 = 0xC0
    COMMAND3 = 0x80
    DSP_ON = 0x08
    COLON_BIT = 0x80

    CHAR_MAP = {
        '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F, '4': 0x66,
        '5': 0x6D, '6': 0x7D, '7': 0x07, '8': 0x7F, '9': 0x6F,
        '-': 0x40, ' ': 0x00
    }

    def __init__(self):
        log.debug("Initializing display controller")
        self.config = Config()
        self._setup_display()
        log.ok("Display controller initialized")

    def _setup_display(self):
        log.info("Setting up display hardware...")
        pins = self.config.get('gpio.display')
        self.clk = DigitalOutputDevice(pins['clk'])
        self.dio = DigitalOutputDevice(pins['dio'])
        self._brightness = self.config.get('display.brightness', 2)
        self._write_data_command()
        self._write_display_control()
        log.ok("Display hardware initialized")

    def _start(self):
        self.dio.on()
        self.clk.on()
        self.dio.off()
        self.clk.off()

    def _stop(self):
        self.clk.off()
        self.dio.off()
        self.clk.on()
        self.dio.on()

    def _write_byte(self, data):
        for _ in range(8):
            self.clk.off()
            self.dio.value = data & 1
            data >>= 1
            self.clk.on()
        
        self.clk.off()
        self.dio.on()
        self.clk.on()
        self.clk.off()

    def _write_data_command(self):
        self._start()
        self._write_byte(self.COMMAND1)
        self._stop()

    def _write_display_control(self):
        self._start()
        self._write_byte(self.COMMAND3 | self.DSP_ON | self._brightness)
        self._stop()

    def update_brightness(self):
        log.debug("Updating display brightness")
        new_brightness = self.config.get('display.brightness', 2)
        if new_brightness != self._brightness:
            self._brightness = new_brightness
            self._write_data_command()
            self._write_display_control()
            log.ok("Display brightness updated")

    def show_number(self, number, colon=False):
        if not isinstance(number, (int, float)):
            return
        
        number = int(number)
        if not -999 <= number <= 9999:
            return
            
        log.debug(f"Displaying number: {number}")
        digits = f"{abs(number):04d}"
        segments = []
        
        if number < 0:
            segments.append(self.CHAR_MAP['-'])
            digits = digits[1:]
        
        segments.extend(self.CHAR_MAP[d] for d in digits)
        self._write_segments(segments, colon)

    def show_time(self, minutes, seconds, colon=True):
        if not isinstance(minutes, int) or not isinstance(seconds, int):
            return
            
        if not (0 <= minutes <= 99 and 0 <= seconds <= 59):
            return

        log.debug(f"Displaying time: {minutes:02d}:{seconds:02d}")
        segments = [
            self.CHAR_MAP[str(minutes // 10)],
            self.CHAR_MAP[str(minutes % 10)],
            self.CHAR_MAP[str(seconds // 10)],
            self.CHAR_MAP[str(seconds % 10)]
        ]
        self._write_segments(segments, colon)

    def _write_segments(self, segments, colon=False):
        self._write_data_command()
        self._start()
        self._write_byte(self.COMMAND2)
        
        for seg in segments:
            if colon:
                seg |= self.COLON_BIT
            self._write_byte(seg)
        
        self._stop()
        self._write_display_control()

    def clear(self):
        log.debug("Clearing display")
        self._write_segments([0, 0, 0, 0])

    def cleanup(self):
        log.info("Shutting down display...")
        self.clear()
        self.clk.close()
        self.dio.close()
        log.ok("Display shutdown complete")

    def show_dashes(self):
        log.debug("Showing dashes")
        segments = [self.CHAR_MAP['-']] * 4
        self._write_segments(segments, False)

    def show_track_total(self, count):
        if not isinstance(count, int) or count < 0 or count > 99:
            return
            
        log.debug(f"Showing track total: {count}")
        segments = [
            self.CHAR_MAP[str(count // 10)],
            self.CHAR_MAP[str(count % 10)],
            self.CHAR_MAP['-'],
            self.CHAR_MAP['-']
        ]
        self._write_segments(segments, False)

    def show_track_number(self, number: int) -> None:
        try:
            number = int(number)
            if not 1 <= number <= 99:
                log.warning(f"Track number out of range: {number}")
                return
            
            log.debug(f"Showing track number: {number}")
            num_str = f"{number:02d}"
            
            segments = [
                self.CHAR_MAP['-'],
                self.CHAR_MAP[num_str[0]],
                self.CHAR_MAP[num_str[1]],
                self.CHAR_MAP['-']
            ]
            
            self._write_segments(segments, False)
            
        except (ValueError, TypeError) as e:
            log.error(f"Invalid track number format: {e}")
            return

    def show_volume(self, number):
        try:
            number = int(number)
            if not 0 <= number <= 100:
                return
                
            log.debug(f"Showing volume: {number}")
            if number == 100:
                segments = [
                    self.CHAR_MAP['-'],
                    self.CHAR_MAP['1'],
                    self.CHAR_MAP['0'],
                    self.CHAR_MAP['0']
                ]
            else:
                num_str = f"{number:02d}"
                segments = [
                    self.CHAR_MAP['-'],
                    self.CHAR_MAP['-'],
                    self.CHAR_MAP[num_str[0]],
                    self.CHAR_MAP[num_str[1]]
                ]
                
            self._write_segments(segments, False)
            
        except (ValueError, TypeError):
            return
