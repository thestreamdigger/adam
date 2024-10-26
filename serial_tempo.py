VERSION = "0.0.1"

import serial
import time
import glob
from mpd import MPDClient, ConnectionError
import json
import signal
import sys

SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1
SERIAL_RETRY_DELAY = 1
MPD_HOST = "localhost"
MPD_PORT = 6600
MPD_RETRY_DELAY = 5
UPDATE_INTERVAL = 0.5
RECONNECT_ATTEMPT_INTERVAL = 0.5
MAX_RECONNECT_ATTEMPTS = 30
RECONNECT_TIMEOUT = 300

class MPDSerialCommunicator:
    def __init__(self):
        self.ser = None
        self.client = None
        self.last_update_time = 0
        self.reconnect_attempts = 0
        self.reconnect_start_time = 0
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def find_pico_port(self):
        ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                return port
            except (OSError, serial.SerialException):
                pass
        return None

    def is_device_available(self):
        return self.find_pico_port() is not None

    def establish_serial_connection(self):
        pico_port = self.find_pico_port()
        if not pico_port:
            print("Pico device not found")
            return False
        try:
            self.ser = serial.Serial(pico_port, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)
            print(f"Serial connection established on {pico_port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {pico_port}: {e}")
            return False

    def establish_mpd_connection(self):
        if self.client:
            try:
                self.client.close()
                self.client.disconnect()
            except Exception:
                pass
        self.client = MPDClient()
        try:
            self.client.connect(MPD_HOST, MPD_PORT)
            print("MPD connection established")
            self.reconnect_attempts = 0
            self.reconnect_start_time = 0
            return True
        except ConnectionError as e:
            print(f"Failed to connect to MPD: {e}")
            return False

    def check_mpd_connection(self):
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def attempt_mpd_reconnection(self):
        if self.reconnect_start_time == 0:
            self.reconnect_start_time = time.time()
        if time.time() - self.reconnect_start_time > RECONNECT_TIMEOUT:
            print(f"Reconnection timeout reached after {RECONNECT_TIMEOUT} seconds. Giving up.")
            return False
        if self.reconnect_attempts >= MAX_RECONNECT_ATTEMPTS:
            print(f"Maximum reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached. Giving up.")
            return False
        self.reconnect_attempts += 1
        print(f"Attempting to reconnect to MPD (Attempt {self.reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS})...")
        time.sleep(MPD_RETRY_DELAY)
        return self.establish_mpd_connection()

    def write_to_pico(self, message):
        try:
            self.ser.write(message.encode('utf-8'))
            return True
        except serial.SerialException as e:
            print(f"Serial write failed: {e}")
            return False

    def read_from_pico(self):
        while self.ser.in_waiting > 0:
            try:
                data = self.ser.readline().decode('utf-8').strip()
                if not data:
                    continue
                message = json.loads(data)
                if message.get('type') == 'command':
                    self.handle_command(message['content'])
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            except Exception as e:
                print(f"Error reading from Pico: {e}")

    def handle_command(self, command):
        action = command.get('action')
        parameters = command.get('parameters', {})
        try:
            if action == 'play_pause':
                self.client.pause()
            elif action == 'next':
                self.client.next()
            elif action == 'previous':
                self.client.previous()
            elif action == 'stop':
                self.client.stop()
            elif action == 'set_volume':
                volume = parameters.get('volume')
                if volume is not None:
                    self.client.setvol(int(volume))
            else:
                print(f"Unknown command: {action}")
        except Exception as e:
            print(f"Error executing command '{action}': {e}")

    def get_mpd_state(self):
        try:
            status = self.client.status()
            current_song = self.client.currentsong() or {}
            playlist = self.client.playlistinfo()
            playlist_length = int(status.get('playlistlength', '0'))
            playlist_total_time = sum(float(song.get('time', 0)) for song in playlist)
            playlist_total_time_str = f"{int(playlist_total_time) // 3600:02d}:{(int(playlist_total_time) % 3600) // 60:02d}:{int(playlist_total_time) % 60:02d}"
            current_playlist_pos = int(status.get('song', '0')) + 1 if 'song' in status else 0
            state = status.get('state', 'stop').upper()
            elapsed = status.get('elapsed')
            total = status.get('duration')
            elapsed_time = int(float(elapsed)) if elapsed else 0
            total_time = int(float(total)) if total else 0
            elapsed_str = f"{elapsed_time // 60:02d}:{elapsed_time % 60:02d}"
            total_str = f"{total_time // 60:02d}:{total_time % 60:02d}"
            state_code = {'PLAY': 'P', 'PAUSE': 'U', 'STOP': 'S'}.get(state, 'S')
            song_id = current_song.get('id', '-1')
            repeat = status.get('repeat', '0')
            random = status.get('random', '0')
            single = status.get('single', '0')
            consume = status.get('consume', '0')
            track = current_song.get('track', '0').split('/')[0].zfill(4)
            artist = current_song.get('artist', 'Unknown Artist')
            title = current_song.get('title', 'Unknown Title')
            album = current_song.get('album', 'Unknown Album')
            genre = current_song.get('genre', 'Unknown Genre')
            year = current_song.get('date', 'Unknown Year')
            file_path = current_song.get('file', '')
            file_extension = file_path.split('.')[-1].upper() if '.' in file_path else 'UNKNOWN'
            audio_info = status.get('audio', '').split(':')
            sample_rate = f"{int(audio_info[0]) / 1000:.1f}kHz" if len(audio_info) > 0 and audio_info[0].isdigit() else "Unknown"
            bit_depth = f"{audio_info[1]}bit" if len(audio_info) > 1 else "Unknown"
            channels = audio_info[2] if len(audio_info) > 2 else "Unknown"
            bitrate = f"{status.get('bitrate', '0')}kbps"
            format = current_song.get('format', 'Unknown')
            outputs = self.client.outputs()
            current_output = next((output for output in outputs if output['outputenabled'] == '1'), {})
            output_name = current_output.get('outputname', 'Unknown')
            stats = self.client.stats()
            uptime = int(stats.get('uptime', 0))
            volume = status.get('volume', 'Unknown')
            return {
                'elapsed': elapsed_str,
                'total': total_str,
                'state': state_code,
                'song_id': song_id,
                'repeat': repeat,
                'random': random,
                'single': single,
                'consume': consume,
                'artist': artist,
                'title': title,
                'album': album,
                'genre': genre,
                'year': year,
                'file_type': file_extension,
                'track_number': track,
                'playlist_position': f"{current_playlist_pos}/{playlist_length}",
                'sample_rate': sample_rate,
                'bit_depth': bit_depth,
                'channels': channels,
                'bitrate': bitrate,
                'format': format,
                'output_name': output_name,
                'uptime': f"{uptime // 86400}d {(uptime % 86400) // 3600}h {(uptime % 3600) // 60}m",
                'volume': volume
            }
        except Exception as e:
            print(f"Error getting MPD state: {e}")
            return None

    def run(self):
        if not self.establish_serial_connection():
            print("Failed to establish serial connection. Exiting...")
            return
        if not self.establish_mpd_connection():
            print("Failed to establish initial MPD connection. Exiting...")
            return
        while True:
            try:
                current_time = time.time()
                if current_time - self.last_update_time < UPDATE_INTERVAL:
                    remaining_time = UPDATE_INTERVAL - (current_time - self.last_update_time)
                    if remaining_time > 0:
                        time.sleep(min(remaining_time, RECONNECT_ATTEMPT_INTERVAL))
                    continue
                if not self.ser or not self.ser.is_open:
                    if not self.establish_serial_connection():
                        time.sleep(SERIAL_RETRY_DELAY)
                        continue
                if not self.check_mpd_connection():
                    print("MPD connection lost. Attempting to reconnect...")
                    if not self.attempt_mpd_reconnection():
                        print("Failed to reconnect to MPD. Exiting...")
                        break
                    continue
                mpd_state = self.get_mpd_state()
                if mpd_state is None:
                    print("Failed to get MPD state. Retrying...")
                    time.sleep(MPD_RETRY_DELAY)
                    continue
                message = {
                    "type": "status",
                    "content": mpd_state
                }
                message_str = json.dumps(message) + '\n'
                if not self.write_to_pico(message_str):
                    print("Failed to write to Pico. Closing serial connection.")
                    self.ser.close()
                    self.ser = None
                    continue
                self.read_from_pico()
                self.last_update_time = current_time
            except Exception as e:
                print(f"Unexpected error: {e}")
                if self.ser:
                    self.ser.close()
                    self.ser = None
                if self.client:
                    try:
                        self.client.close()
                        self.client.disconnect()
                    except Exception:
                        pass
                    self.client = None
                time.sleep(SERIAL_RETRY_DELAY)

    def signal_handler(self, signal, frame):
        print("Program interrupted by user. Exiting...")
        if self.ser:
            self.ser.close()
        if self.client:
            try:
                self.client.close()
                self.client.disconnect()
            except Exception:
                pass
        sys.exit(0)

if __name__ == "__main__":
    communicator = MPDSerialCommunicator()
    communicator.run()
