# Adam for MPD

## Overview

Adam is my DIY project that brings a touch of nostalgia to modern music playback. Sometimes we just want to sit back, watch time tick by on a display, and enjoy our music - just like we used to do with old CD players. That's exactly what Adam does: it adds a simple yet charming visual interface to a Raspberry Pi running moOde audio player. Inspired by the classic CD players I grew up with, Adam provides basic visual feedback about music playback using a 4-digit 7-segment LED display, five indicator LEDs, and a push button.

## Core Components

1. **Visual Feedback**:
   - 4-digit 7-segment LED display (TM1637) showing:
     - Track numbers (format: '-XX-')
     - Playback time (elapsed or remaining)
     - Volume levels (format: '--XX')
   - Five status LEDs indicating MPD states:
     - Repeat
     - Random
     - Single
     - Consume
     - Copy (new: indicates USB copy operations)

2. **Controls**:
   - Push button with multiple functions:
     - Short press: Activates "roulette" mode (random playback)
     - Long press: System shutdown

3. **New Features**:
   - **Adam Go**: Quick USB copy of currently playing album
     - Automatic USB drive detection
     - Configurable directory structure preservation
     - Visual feedback through copy LED
     - Disk space verification support

## Configuration

All settings are centralized in `config/settings.json`. Key configurations include:

- GPIO pin assignments
- Display settings (brightness, mode)
- Timing parameters
- USB copy settings:
  - Minimum USB drive size
  - Directory structure
  - Skip folders

## Installation

1. Install [moOde](https://moodeaudio.org/) on your Raspberry Pi

2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/adam.git
   cd adam
   ```

3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   .\venv\Scripts\activate  # On Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
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

- `scripts/adam_go.py`: Initiates current album copy to USB
- `scripts/roulette.sh`: Activates random playback mode
- `scripts/roulette_album.sh`: Random album playback
- `scripts/shutdown.sh`: Safe system shutdown
- `scripts/toggle_scripts/`: System state toggle scripts

## Version and Compatibility

- Current version: 0.3
- Tested with:
  - moOde audio player 8.3.9
  - Raspberry Pi 4 Model B (compatible with other models)
  - Python 3.7+

## Acknowledgments

- [moOde audio player](https://moodeaudio.org/)
- [MPD (Music Player Daemon)](https://www.musicpd.org/)
- [TM1637 documentation](https://www.makerguides.com/wp-content/uploads/2019/08/TM1637-Datasheet.pdf)

## License

This project is free to use.
