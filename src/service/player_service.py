import time
import signal
import os
import sys
from src.core.config import Config
from src.core.mpd_client import MPDClient
from src.hardware.led.controller import LEDController
from src.hardware.display.tm1637 import TM1637
from src.hardware.button.controller import ButtonController
from src.utils.logger import Logger

log = Logger()

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

DISPLAY_MODES = {
    'ELAPSED': 'elapsed',
    'REMAINING': 'remaining'
}

class PlayerService:
    def __init__(self):
        log.debug("Initializing player service")
        self.config = Config()
        self.mpd = MPDClient()
        
        log.info("Setting up hardware controllers...")
        self.led_controller = LEDController()
        self.display = TM1637()
        self.display.show_dashes()
        self.button_controller = ButtonController()
        
        self.running = False
        self.last_config_check = 0
        self.last_song_id = None
        
        log.info("Loading service configurations...")
        self._load_config()
        log.ok("Player service initialized")

    def _load_config(self):
        log.debug("Loading service configuration")
        self.display_mode = self.config.get('display.mode', DISPLAY_MODES['ELAPSED'])
        self.last_volume = None
        self.volume_display_until = 0
        self.colon_state = False
        self.default_update_interval = self.config.get('timing.update_interval', 1)
        self.volume_update_interval = self.config.get('timing.volume_update_interval', 0.1)
        self.stop_display_state = 0
        self.stop_state_changed_at = 0
        self.track_display_until = 0
        self.pause_last_toggle = 0
        self._load_display_config()

    def _load_display_config(self):
        log.debug("Loading display configuration")
        self._load_stop_mode_config()
        self.pause_blink_interval = self.config.get('display.pause_mode.blink_interval', 1)
        self.track_number_time = self.config.get('display.play_mode.track_number_time', 2)

    def _load_stop_mode_config(self):
        self.stop_mode_times = {
            'symbol': self.config.get('display.stop_mode.stop_symbol_time', 2),
            'tracks': self.config.get('display.stop_mode.track_total_time', 2),
            'total': self.config.get('display.stop_mode.playlist_time', 2)
        }

    def _handle_config_update(self):
        log.info("Processing configuration update")
        
        self.display_mode = self.config.get('display.mode', DISPLAY_MODES['ELAPSED'])
        self._load_display_config()
        
        status = self.mpd.get_status()
        if status:
            self._update_display(status)

    def _update_stop_display(self):
        current_time = time.time()
        
        current_duration = self.stop_mode_times.get(
            ['symbol', 'tracks', 'total'][self.stop_display_state], 
            2
        )
        
        if current_time - self.stop_state_changed_at >= current_duration:
            self.stop_display_state = (self.stop_display_state + 1) % 3
            self.stop_state_changed_at = current_time
            log.debug(f"Stop display state changed to {self.stop_display_state}")
        
        playlist_info = self.mpd.get_playlist_info()
        
        if self.stop_display_state == 0:
            self.display.show_dashes()
        elif self.stop_display_state == 1:
            self.display.show_track_total(playlist_info['total_tracks'])
        elif self.stop_display_state == 2:
            total_time = sum(
                float(track.get('duration', 0)) 
                for track in playlist_info['tracks']
            )
            minutes = int(total_time) // 60
            seconds = int(total_time) % 60
            self.display.show_time(minutes, seconds, True)

    def _check_track_change(self, current_song):
        if not current_song:
            return
        
        song_id = current_song.get('id', '0')
        track_number = current_song.get('track', '0')
        
        track_config = self.config.get('display.play_mode.track_number', {})
        show_number = track_config.get('show_number', True)
        display_time = track_config.get('display_time', 2)

        if show_number and ((song_id and song_id != self.last_song_id) or 
                          (not hasattr(self, '_last_state') or self._last_state != 'play')):
            self.last_song_id = song_id
            
            if track_number.isdigit():
                track_num = int(track_number)
                if 1 <= track_num <= 99:
                    log.debug(f"Track changed to {track_num}")
                    self.track_display_until = time.time() + display_time
                    self.display.show_track_number(track_num)

    def _update_pause_display(self, elapsed_time, total_time):
        phase = int(time.time() / self.pause_blink_interval) % 2
        
        if phase == 0:
            try:
                if self.display_mode == DISPLAY_MODES['REMAINING'] and total_time != 'N/A':
                    time_value = float(total_time) - float(elapsed_time)
                else:
                    time_value = float(elapsed_time)
                
                minutes, seconds = self._convert_time_to_minutes_seconds(time_value)
                if minutes is not None:
                    self.display.show_time(minutes, seconds, True)
                else:
                    self.display.show_dashes()
            except (ValueError, TypeError):
                self.display.show_dashes()
        else:
            self.display.clear()

    def _convert_time_to_minutes_seconds(self, time_value):
        try:
            time_float = float(time_value)
            minutes = int(time_float) // 60
            seconds = int(time_float) % 60
            return minutes, seconds
        except (ValueError, TypeError):
            return None, None

    def _update_time_display(self, elapsed_time, total_time):
        try:
            if self.display_mode == DISPLAY_MODES['REMAINING'] and total_time != 'N/A':
                time_value = float(total_time) - float(elapsed_time)
            else:
                time_value = float(elapsed_time)
            
            minutes, seconds = self._convert_time_to_minutes_seconds(time_value)
            if minutes is not None:
                self.display.show_time(minutes, seconds, True)
            else:
                self.display.show_dashes()
        except (ValueError, TypeError):
            self.display.show_dashes()

    def _update_display(self, status):
        current_time = time.time()
        state = status.get('state', 'stop')
        
        if current_time < self.volume_display_until:
            current_volume = int(status.get('volume', '0'))
            self.display.show_volume(current_volume)
            return
        
        elapsed_time = status.get('elapsed', '0')
        total_time = status.get('duration', '0')
        
        if state == 'play':
            current_song = self.mpd.get_current_song()
            self._check_track_change(current_song)
            
            if current_time >= self.track_display_until:
                self._update_time_display(elapsed_time, total_time)
            
        elif state == 'pause':
            self._update_pause_display(elapsed_time, total_time)
        elif state == 'stop':
            if not hasattr(self, '_last_state') or self._last_state != 'stop':
                self.stop_display_state = 0
                self.stop_state_changed_at = current_time
            self._update_stop_display()
        
        self._last_state = state

    def show_volume(self, status):
        try:
            current_volume = int(status.get('volume', '0'))
            log.debug(f"Displaying volume: {current_volume}")
            self.display.show_volume(current_volume)
            self.volume_display_until = time.time() + self.config.get('timing.volume_display_duration', 3)
        except (ValueError, TypeError):
            return

    def _check_config_updates(self):
        current_time = time.time()
        update_config = self.config.get('updates.trigger', {})
        check_interval = update_config.get('check_interval', 1)
        trigger_file = update_config.get('file', '.update_trigger')
        debounce_time = update_config.get('debounce_time', 0.1)
        
        if (current_time - self.last_config_check) >= check_interval:
            trigger_path = os.path.join(PROJECT_ROOT, 'config', trigger_file)
            if os.path.exists(trigger_path):
                log.debug("Configuration update triggered")
                
                time.sleep(debounce_time)
                
                self.config.load_config()
                
                new_brightness = self.config.get('display.brightness')
                new_display_mode = self.config.get('display.mode')
                
                if new_brightness != self.display._brightness:
                    log.debug("Updating brightness")
                    self.display.update_brightness()
                    self.led_controller._setup_leds()
                
                if new_display_mode != self.display_mode:
                    log.debug("Updating display mode")
                    self.display_mode = new_display_mode
                    status = self.mpd.get_status()
                    if status:
                        self._update_display(status)
                
                os.unlink(trigger_path)
            self.last_config_check = current_time

    def start(self):
        log.info("Starting player service")
        log.wait("Waiting for MPD connection...")
        self.running = True
        
        def handle_signal(signum, frame):
            log.info("Received shutdown signal")
            self.running = False
        
        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)

        try:
            while self.running:
                start_time = time.time()
                
                self._check_config_updates()
                
                status = self.mpd.get_status()
                if status:
                    self.led_controller.update_from_mpd_status(status)
                    
                    current_volume = status.get('volume', '0')
                    if current_volume != self.last_volume:
                        self.show_volume(status)
                        self.last_volume = current_volume
                    
                    self._update_display(status)
                
                current_time = time.time()
                update_interval = (self.volume_update_interval 
                                 if current_time < self.volume_display_until 
                                 else self.default_update_interval)
                
                elapsed = time.time() - start_time
                sleep_time = max(0, update_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        finally:
            self.cleanup()

    def cleanup(self):
        log.info("Shutting down player service")
        self.led_controller.cleanup()
        self.display.cleanup()
        self.button_controller.cleanup()
        self.mpd.close()
        log.ok("Player service shutdown complete")
