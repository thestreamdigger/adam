import os
from mpd import MPDClient, CommandError

MPD_HOST = 'localhost'
MPD_PORT = 6600

def load_album_and_start_playback():
    os.system('sudo pkill -f roulette.sh')
    os.system('sudo pkill -f ashuffle')

    client = MPDClient()
    try:
        client.connect(MPD_HOST, MPD_PORT)
        current_song = client.currentsong()
        if not current_song:
            return

        album = current_song.get('album')
        if not album:
            return

        album_artist = current_song.get('albumartist', current_song.get('artist'))
        if not album_artist:
            return

        songs = client.search('album', album, 'albumartist', album_artist)
        if not songs:
            return

        songs_sorted = sorted(
            songs, 
            key=lambda x: (int(x.get('disc', 1)), int(x.get('track', 0)))
        )

        client.clear()
        for song in songs_sorted:
            if 'file' in song:
                client.add(song['file'])

        client.consume(0)
        client.play()
    except CommandError:
        pass
    except Exception:
        pass
    finally:
        client.close()
        client.disconnect()

load_album_and_start_playback()
