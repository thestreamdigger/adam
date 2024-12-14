from mpd import MPDClient as BaseMPDClient
import time
from src.utils.logger import Logger

log = Logger()

class MPDClient:
    def __init__(self, host='localhost', port=6600):
        self.host = host
        self.port = port
        self._client = BaseMPDClient()
        self._connected = False
        self._last_try = 0
        self._retry_interval = 5
        log.debug(f"MPD client initialized for {host}:{port}")

    def connect(self):
        current_time = time.time()
        if not self._connected and (current_time - self._last_try) >= self._retry_interval:
            try:
                log.wait("Attempting to connect to MPD...")
                self._client.connect(self.host, self.port)
                self._connected = True
                log.ok(f"Connected to MPD at {self.host}:{self.port}")
                return True
            except:
                self._connected = False
                self._last_try = current_time
                log.error(f"Failed to connect to MPD at {self.host}:{self.port}")
        return self._connected

    def get_status(self):
        try:
            if self.connect():
                status = self._client.status()
                log.debug(f"MPD status: {status}")
                return status
        except:
            self._connected = False
            log.error("Failed to get MPD status")
        return None

    def get_current_song(self):
        try:
            if self.connect():
                song = self._client.currentsong()
                log.debug(f"Current song: {song}")
                return song
        except:
            self._connected = False
            log.error("Failed to get current song")
        return None

    def close(self):
        if self._connected:
            try:
                log.debug("Closing MPD connection")
                self._client.close()
                self._client.disconnect()
                log.ok("MPD connection closed")
            except:
                log.error("Error closing MPD connection")
            finally:
                self._connected = False

    def get_playlist_info(self):
        try:
            if self.connect():
                status = self._client.status()
                playlist = self._client.playlistinfo()
                log.debug(f"Playlist info retrieved: {len(playlist)} tracks")
                return {
                    'total_tracks': int(status.get('playlistlength', 0)),
                    'tracks': playlist
                }
        except:
            self._connected = False
            log.error("Failed to get playlist info")
        return {'total_tracks': 0, 'tracks': []}

