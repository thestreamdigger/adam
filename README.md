# Adam: digital retro charm

## Overview

Adam is my DIY project that brings a touch of nostalgia to modern music playback. It adds a simple, yet charming visual interface to a Raspberry Pi running moOde audio player. Inspired by the classic CD players I grew up with, Adam provides basic visual feedback about music playback using a 4-digit 7-segment LED display, five indicator LEDs, and a rotary encoder.

The main components I've put together are:
1. A 4-digit 7-segment LED display (controlled by a TM1637 chip) showing track numbers, playback time, or volume.
2. Four LEDs indicating MPD states: Single, Random, Repeat, and Consume.
3. One LED for indicating errors or connection issues.
4. A rotary encoder with an integrated push button for volume control and additional actions.

Adam doesn't modify moOde's excellent audio functionality. Instead, it offers a way for me (and now you) to view essential playback information without using a screen or web interface, adding a digital retro-style visual element to the moOde system.

## Motivation

As I embraced Single Board Computers (SBCs) for music playing, I found myself missing the simple act of watching seconds tick by while listening to music. While my mobile screen overwhelmed me with constant streams of unrelated information, a bare Raspberry Pi setup left me craving for some visual feedback. 

Adam was born from this desire to strike a personal balance. It brings me back to a more tangible and focused way of interacting with my FLAC music library. This project also marks my first significant venture into Python programming, allowing me to create a physical interface that enhances engagement of my personal music playback experience.

## Features and Functionality

Adam's display functionality varies based on the playback state, much like the CD players of old:

1. **Play State**: 
   - Displays elapsed time or remaining time for the current track (you can change it on-the-fly)
   - Shows the track number for the first few seconds when a new track starts (I made this duration configurable in `tempo.cfg`).

2. **Pause State**:
   - The time display blinks, reminding me that the music is just waiting to continue.

3. **Stop State**:
   - Cycles through a carousel of information:
     - Total number of tracks in the current playlist.
     - Total playback time of all tracks in the playlist.

I faced the challenge of displaying comprehensive information on a simple 4-digit display. It was a fun puzzle to solve, and now Adam cleverly switches between showing track numbers, minutes, and seconds to provide maximum information within the limited space.

### Unique Features

1. **Status Visualization**:
   - Four LEDs clearly display the current MPD states: Single, Random, Repeat, and Consume.
   - An additional LED indicates any errors or issues with the MPD connection.
   - The 7-segment display shows track numbers, elapsed time, remaining time, and total time, just like my old CD player.

2. **Display Modes**:
   - You can toggle between displaying elapsed time and remaining time.
   - I added three brightness levels that you can adjust on-the-fly.

3. **Volume Visualization**:
   - Volume changes are immediately displayed, giving that satisfying visual feedback.

4. **Playback Mode Indication**:
   - I created two scripts for some fun randomization:
     - `roulette.sh`: Randomly loads individual tracks from your collection.
     - `roulette-album.sh`: Randomly loads entire albums, like a personal jukebox.

5. **Safe Shutdown**:
   - Adam detects when the system is shutting down and clears all displays for a clean power-off.

## Hardware Setup

### Components I Used
- Raspberry Pi
- 4-Digit 7-Segment LED Display (controlled by TM1637 chip)
- 5 LEDs
- Rotary Encoder with integrated push button

### GPIO Configuration
Here's how I set up the GPIO pins in `tempo.py`:
```python
CLK_GPIO = 15
DIO_GPIO = 14
```
Note: The rotary encoder is configured directly in moOde's Audio settings.

## Usage

1. First, install moOde Audio Player on your Raspberry Pi.
2. Clone this repository to your Pi.
3. Connect all the hardware components (I'm working on a detailed schematic to share soon).
4. Edit `tempo.cfg` to match your setup and preferences.
5. To start Adam, run these two scripts:
   ```
   sudo python3 tempo.py
   sudo python3 control.py
   sudo python3 button-control.py
   ```

I recommend setting up systemd services for automatic startup. I've included detailed instructions in the INSTALL.md file.

## Remote Control Integration

In my personal setup, I use a FLIRC USB dongle, which lets me use an infrared remote control. I highly recommend it for its versatility. You can find instructions for setting it up with moOde in their forum.

## Contributions

While Adam started as a personal project, I'm excited to share it with the community. Feel free to explore, modify, and enhance it to fit your needs. I'd love to see how others might expand on this idea!

## Author's Note

Adam is my first major project in Python and my first DIY project of this scale. Bringing this project to life has been a significant personal achievement for me. I hope it inspires you to find creative ways to interact with your digital music collection and maybe even contribute to a vibrant community of audio enthusiasts and DIY creators.

## Acknowledgments

A big thank you to the moOde audio player project. Their outstanding audio platform and commitment to open-source principles really inspires me.

## License

I'm releasing this project under the GNU General Public License v3.0. If you distribute this software or any derivative works, you must do so under the same license (GPL-3.0).

## Version and Compatibility

Current version: 1.0

I've tested this with moOde audio player version 8.3.9
