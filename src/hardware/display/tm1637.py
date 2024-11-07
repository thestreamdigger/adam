from gpiozero import DigitalOutputDevice
import time
from core.config import Config

class TM1637:
    """TM1637 LED display controller with real-time config updates"""
    # Display command bytes
    COMMAND1 = 0x40
    COMMAND2 = 0xC0
    COMMAND3 = 0x80
    DSP_ON = 0x08
    COLON_BIT = 0x80

    # Character bit mappings
    CHAR_MAP = {
        '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F, '4': 0x66,
        '5': 0x6D, '6': 0x7D, '7': 0x07, '8': 0x7F, '9': 0x6F,
        '-': 0x40, ' ': 0x00
    }

    def __init__(self):
        self.config = Config()
        self._setup_display()
        self.config.add_observer(self.update_brightness)

    def _setup_display(self):
        """Initialize display with current config"""
        pins = self.config.get('gpio.display')
        self.clk = DigitalOutputDevice(pins['clk'])
        self.dio = DigitalOutputDevice(pins['dio'])
        self._brightness = self.config.get('display.brightness', 2)
        self._write_data_command()
        self._write_display_control()

    def _start(self):
        """Send start signal"""
        self.dio.on()
        self.clk.on()
        self.dio.off()
        self.clk.off()

    def _stop(self):
        """Send stop signal"""
        self.clk.off()
        self.dio.off()
        self.clk.on()
        self.dio.on()

    def _write_byte(self, data):
        """Write a byte to display"""
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
        """Write data command"""
        self._start()
        self._write_byte(self.COMMAND1)
        self._stop()

    def _write_display_control(self):
        """Write display control command"""
        self._start()
        self._write_byte(self.COMMAND3 | self.DSP_ON | self._brightness)
        self._stop()

    def update_brightness(self):
        """Update brightness from config"""
        new_brightness = self.config.get('display.brightness', 2)
        if new_brightness != self._brightness:
            self._brightness = new_brightness
            self._write_data_command()
            self._write_display_control()

    def show_number(self, number, colon=False):
        """Display a number"""
        if not isinstance(number, (int, float)):
            return
        
        number = int(number)
        if not -999 <= number <= 9999:
            return

        digits = f"{abs(number):04d}"
        segments = []
        
        if number < 0:
            segments.append(self.CHAR_MAP['-'])
            digits = digits[1:]
        
        segments.extend(self.CHAR_MAP[d] for d in digits)
        self._write_segments(segments, colon)

    def show_time(self, minutes, seconds, colon=True):
        """Display time"""
        if not isinstance(minutes, int) or not isinstance(seconds, int):
            return
            
        if not (0 <= minutes <= 99 and 0 <= seconds <= 59):
            return

        segments = [
            self.CHAR_MAP[str(minutes // 10)],
            self.CHAR_MAP[str(minutes % 10)],
            self.CHAR_MAP[str(seconds // 10)],
            self.CHAR_MAP[str(seconds % 10)]
        ]
        self._write_segments(segments, colon)

    def _write_segments(self, segments, colon=False):
        """Write segments to display"""
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
        """Clear display"""
        self._write_segments([0, 0, 0, 0])

    def cleanup(self):
        """Cleanup resources"""
        self.config.remove_observer(self.update_brightness)
        self.clear()
        self.clk.close()
        self.dio.close()

    def show_dashes(self):
        """Display four dashes (----) on the display"""
        segments = [self.CHAR_MAP['-']] * 4
        self._write_segments(segments, False)

    def show_track_total(self, count):
        """Display total track count in format 'NN--'"""
        if not isinstance(count, int) or count < 0 or count > 99:
            return
            
        segments = [
            self.CHAR_MAP[str(count // 10)],
            self.CHAR_MAP[str(count % 10)],
            self.CHAR_MAP['-'],
            self.CHAR_MAP['-']
        ]
        self._write_segments(segments, False)

    def show_track_number(self, number: int) -> None:
        """Display track number in format '-NN-'
        Args:
            number: track number (1-99)
        Example:
            Track 1  shows as '-01-'
            Track 12 shows as '-12-'
        """
        try:
            number = int(number)
            if not 1 <= number <= 99:
                return
            
            # Format number with leading zero
            num_str = f"{number:02d}"  # Garante dois dígitos
            
            segments = [
                self.CHAR_MAP['-'],      # Primeiro traço
                self.CHAR_MAP[num_str[0]], # Primeiro dígito
                self.CHAR_MAP[num_str[1]], # Segundo dígito
                self.CHAR_MAP['-']       # Último traço
            ]
            
            self._write_segments(segments, False)
            
        except (ValueError, TypeError):
            return

    def show_volume(self, number):
        """Display volume in format '--NN'
        Args:
            number: volume (0-100)
        Example:
            5   -> '--05'
            10  -> '--10'
            100 -> '-100'
        """
        try:
            number = int(number)
            if not 0 <= number <= 100:
                return
                
            if number == 100:
                segments = [
                    self.CHAR_MAP['-'],
                    self.CHAR_MAP['1'],
                    self.CHAR_MAP['0'],
                    self.CHAR_MAP['0']
                ]
            else:
                # Format number with leading zero
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
