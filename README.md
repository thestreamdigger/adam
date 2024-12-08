# Adam for MPD

## Overview

Adam is my DIY project that brings a touch of nostalgia to modern music playback. Sometimes we just want to sit back, watch time tick by on a display, and enjoy our music - just like we used to do with old CD players. That's exactly what Adam does: it adds a simple yet charming visual interface to a Raspberry Pi running moOde audio player. Inspired by the classic CD players I grew up with, Adam provides basic visual feedback about music playback using a 4-digit 7-segment LED display, five indicator LEDs, and a push button.

## Core Components

1. **Visual Feedback**:
   - 4-digit 7-segment LED display (TM1637) showing:
     - Track numbers (format: '-XX-')
     - Playback time (elapsed or remaining)
     - Volume levels (format: '--XX')
   - Five status LEDs indicating:
     - Repeat mode
     - Random mode
     - Single mode
     - Consume mode
     - USB Copy status

2. **Controls**:
   - Push button with multiple functions:
     - Short press: Activates "roulette" mode (random playback)
     - Long press: System shutdown
     - Double press: Initiates USB album copy (when USB drive is detected)

3. **USB Copy Features**:
   - Quick copy of currently playing album to USB drive
   - Smart USB drive detection and mounting
   - Automatic directory structure preservation
   - Visual feedback through dedicated status LED:
     - Solid: Copy in progress
     - Blinking: Error occurred
     - Off: Ready for new operation
   - Free space verification before copy

## Configuration

All settings are centralized in `config/settings.json`. Key configurations include:

- GPIO pin assignments
- Display settings (brightness, mode)
- Timing parameters
- USB copy settings:
  - Minimum required USB drive size
  - Directory structure preservation options
  - Skip patterns for files/folders
  - Target directory structure
  - Copy verification options

## Installation

1. Install [moOde](https://moodeaudio.org/) on your Raspberry Pi

2. Clone this repository:
   ```bash
   git clone https://github.com/thestreamdigger/adam-mpd.git
   cd adam-mpd
   ```

3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -e .
   ```

5. Configure your GPIO pins in `config/settings.json`

6. Start the service:
   ```bash
   python3 src/main.py
   ```

### Service Installation

To run Adam as a system service:

1. Copy the service file:
   ```bash
   sudo cp install/adam.service /etc/systemd/system/
   ```
2. Enable and start the service:
   ```bash
   sudo systemctl enable adam
   sudo systemctl start adam
   ```

## Utility Scripts

- `scripts/adam_go.py`: Quick copy of current album to USB
- `scripts/roulette.sh`: Activates random playback mode
- `scripts/roulette_album.sh`: Random album playback
- `scripts/shutdown.sh`: Safe system shutdown
- `scripts/toggle_scripts/`: Various toggle scripts for system states

## Using USB Copy Feature

1. Insert a USB drive (minimum size configurable in settings)
2. While music is playing, double-press the button or run `adam_go.py`
3. The Copy LED will light up during the transfer
4. When the LED turns off, your music is ready on the USB drive
5. Check the system logs for any copy details or errors

## Version and Compatibility

- Current version: 0.4
- Tested with:
  - moOde audio player 8.3.9
  - Raspberry Pi 4 Model B (compatible with other models)
  - Python 3.7+
  - Various USB drives (FAT32, NTFS, exFAT)

## Acknowledgments

- [moOde audio player](https://moodeaudio.org/)
- [MPD (Music Player Daemon)](https://www.musicpd.org/)
- [TM1637 documentation](https://www.makerguides.com/wp-content/uploads/2019/08/TM1637-Datasheet.pdf)

## License

This project is free to use.
