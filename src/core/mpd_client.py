from mpd import MPDClient as BaseMPDClient
import time

class MPDClient:
    def __init__(self, host='localhost', port=6600):
        self.host = host
        self.port = port
        self._client = BaseMPDClient()
        self._connected = False
        self._last_try = 0
        self._retry_interval = 5

    def connect(self):
        current_time = time.time()
        if not self._connected and (current_time - self._last_try) >= self._retry_interval:
            try:
                self._client.connect(self.host, self.port)
                self._connected = True
                return True
            except:
                self._connected = False
                self._last_try = current_time
        return self._connected

    def get_status(self):
        try:
            if self.connect():
                return self._client.status()
        except:
            self._connected = False
        return None

    def get_current_song(self):
        try:
            if self.connect():
                return self._client.currentsong()
        except:
            self._connected = False
        return None

    def close(self):
        if self._connected:
            try:
                self._client.close()
                self._client.disconnect()
            finally:
                self._connected = False

    def get_playlist_info(self):
        try:
            if self.connect():
                status = self._client.status()
                playlist = self._client.playlistinfo()
                return {
                    'total_tracks': int(status.get('playlistlength', 0)),
                    'tracks': playlist
                }
        except:
            self._connected = False
        return {'total_tracks': 0, 'tracks': []}

