# Adam: Digital Retro Charm for moOde

## Overview

Adam is my DIY project that brings a touch of nostalgia to modern music playback. It adds a simple, yet charming visual interface to a Raspberry Pi running moOde audio player. Inspired by the classic CD players I grew up with, Adam provides basic visual feedback about music playback using a 4-digit 7-segment LED display, four indicator LEDs, and a rotary encoder with push button.

## Core Components

1. **Visual Feedback**:
   - 4-digit 7-segment LED display (TM1637) showing:
     - Track numbers (format: '-XX-')
     - Playback time (elapsed or remaining)
     - Volume levels (format: '--XX')
   - Four status LEDs indicating MPD states:
     - Repeat
     - Random
     - Single
     - Consume

2. **Physical Controls**:
   - Rotary encoder with push button:
     - Rotation: Volume control
     - Short press: Toggle roulette mode
     - Long press: System shutdown

## Project Structure

```
├── config/
│   └── settings.json         # Centralized configuration
├── scripts/
│   ├── roulette.sh          # Random track playback
│   ├── roulette_album.sh    # Random album playback
│   ├── shutdown.sh          # Safe system shutdown
│   └── toggle_scripts/      # State toggle controls
│       ├── toggle_brightness.py    # Toggle display brightness
│       ├── toggle_consume.sh       # Toggle consume mode
│       ├── toggle_display.py       # Toggle time display mode
│       ├── toggle_headless.sh      # Toggle service
│       ├── toggle_random.sh        # Toggle random mode
│       ├── toggle_repeat.sh        # Toggle repeat mode
│       └── toggle_single.sh        # Toggle single mode
├── src/
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration manager
│   │   └── mpd_client.py    # MPD client wrapper
│   ├── hardware/            # Hardware interface
│   │   ├── button/         # Button controller
│   │   ├── display/        # TM1637 display driver
│   │   └── led/            # LED controller
│   ├── service/            # Main service logic
│   │   └── player_service.py # Main service coordinator
│   └── main.py             # Application entry point
```

## Features

### Display Modes

1. **Play State**: 
   - Time display (configurable):
     - Elapsed time (e.g., "12:34")
     - Remaining time (e.g., "02:15")
   - Track number display (e.g., "-01-")
   - Volume level indication (e.g., "--45")

2. **Pause State**:
   - Blinking time display

3. **Stop State**:
   - Rotating display showing:
     - Stop symbol (----)
     - Total tracks (XX--)
     - Total playlist time

### Smart Features

1. **Real-time Configuration**:
   - Dynamic settings updates
   - Three brightness levels (0, 2, 6)
   - Configurable display modes

2. **Playback Modes**:
   - Standard playback
   - Random track roulette
   - Random album roulette (maintains album track order)

3. **System Integration**:
   - Safe shutdown handling
   - MPD state monitoring
   - Automatic reconnection
   - Volume control via rotary encoder

## Hardware Setup

### Required Components
- Raspberry Pi
- TM1637 4-digit display
- 4 status LEDs
- Rotary encoder with push button (KY-040 or similar)
- Appropriate resistors

### GPIO Configuration
Default GPIO assignments in `config/settings.json`:
```json
{
  "gpio": {
    "button": 16,
    "display": {
      "clk": 15,
      "dio": 14
    },
    "leds": {
      "repeat": 17,
      "random": 27,
      "single": 22,
      "consume": 10
    }
  }
}
```

## Installation

1. Install [moOde](https://moodeaudio.org/) on your Raspberry Pi
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/adam.git
   cd adam
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your GPIO pins in `config/settings.json`
5. Start the service:
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

## Configuration

All settings are centralized in `config/settings.json`. Key configurations include:

- GPIO pin assignments
- Display settings (brightness, mode)
- Timing parameters
- Script paths

## Version and Compatibility

- Current version: 0.2
- Tested with:
  - moOde audio player 8.3.9
  - Raspberry Pi 4 Model B (compatible with other models)
  - Python 3.7+

## Acknowledgments

- [moOde audio player](https://moodeaudio.org/)
- [MPD (Music Player Daemon)](https://www.musicpd.org/)
- [TM1637 documentation](https://www.makerguides.com/wp-content/uploads/2019/08/TM1637-Datasheet.pdf)

## License

This project is licensed under the MIT License - see the LICENSE file for details.