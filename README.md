# Adam for moOde audio player

## Overview & Background
Adam is a Python project that blends hardware and software to recreate a **CD player-style interface** on a Raspberry Pi running moOde audio player. The setup features a 4-digit 7-segment LED display, five indicator LEDs, and a single push button—just enough for that straightforward, track-and-time display we all know from traditional CD players. I started this as a hobby while I was getting into Python, fueled by my passion for digital music playback and the desire for a device that shows time and track info the way I like.

## What Has Been Achieved
Over the last couple of years, Adam has grown along with my Python skills, guided by the idea that music can be both high-tech and visually intuitive. In the beginning, it was just a single script controlling a TM1637 display, back when I only knew the basics. Because this is a physical build, I've stuck with the hardware design I had in mind from the start: a few LEDs for MPD status, a time display, and simple playback controls.

## Bottlenecks
Developing a GPIO controller on the Raspberry Pi comes with its challenges. Despite having 40 pins, only four support hardware PWM, and two of those are used for i2s audio output. This can complicate things if you want to dim LEDs while also planning to run a DAC off the same Pi. I chose to use USB audio output, which influences some of my design decisions. 

Along the way, I discovered microcontrollers like the Raspberry Pi Pico (RP2040), which are affordable and very flexible for tasks like PWM control. Initially, I planned to stick solely to the Pi, but exploring these other controllers has shown me just how many options are out there.

## Future Development
Adam’s code can be adapted for different uses, though it’s currently tied to the Pi’s GPIO and my personal approach. In time, I'd like to create something that other tinkerers and audio enthusiasts can build upon—especially since many single-board computers have USB outputs suited for music streaming. There's a lot of potential to expand.

For now, development will likely focus on bug fixes or new ideas I pick up when I have time to refactor. Hopefully, you’ll find something in Adam that inspires your own project—building physical devices is tricky, but incredibly rewarding once it all comes together.

## Features

### Visual Interface
- **4-digit LED Display (TM1637)**
  - Track numbers (`-XX-`)
  - Playback time (`MM:SS`)
  - Volume levels (`--XX`)
  - Multiple brightness levels

- **Status LEDs**
  - Hardware PWM-enabled indicators
  - Synchronized brightness control
  - Playback mode indicators
  - USB operation status

### Controls
- **Multi-function Button**
  - Short press: Random playback
  - Long press: System shutdown
  - Double press: USB copy (when available)

### Smart USB Operations
- **Quick Album Copy**
  - Automatic USB detection
  - Directory structure preservation
  - Progress display
  - Error handling

### Advanced Features
- **Real-time Configuration**
  - No restart required
  - Dynamic display modes
  - Adjustable brightness
  - Customizable timings

# Technical Manual

## Table of Contents
1. [Hardware Setup](#hardware-setup)
2. [GPIO Pinout](#gpio-pinout)
3. [Hardware Components](#hardware-components)
4. [Project Structure](#project-structure)
5. [Configuration](#configuration)
6. [Features & Usage](#features--usage)
7. [Service Installation](#service-installation)
8. [Troubleshooting](#troubleshooting)

## Hardware Setup

### Required Components
- Raspberry Pi (tested on Model 4B)
- TM1637 4-digit 7-segment display
- 5x LEDs (4 PWM-capable + 1 standard)
- 1x Momentary push button
- Optional: Rotary encoder with push button
- Resistors and jumper wires

### GPIO Pinout

```
                 Raspberry Pi
                  +--------+
       3.3V  [1]  | o    o |  [2]  5V
 SDA1/GPIO2  [3]  | o    o |  [4]  5V
 SCL1/GPIO3  [5]  | o    o |  [6]  GND
      GPIO4  [7]  | o    o |  [8]  GPIO14 (Display DIO)
        GND  [9]  | o    o |  [10] GPIO15 (Display CLK)
     GPIO17 [11]  | o    o |  [12] GPIO18 (Single LED)*
     GPIO27 [13]  | o    o |  [14] GND
     GPIO22 [15]  | o    o |  [16] GPIO23 (Encoder A)
       3.3V [17]  | o    o |  [18] GPIO24 (Encoder B)
     GPIO10 [19]  | o    o |  [20] GND
      GPIO9 [21]  | o    o |  [22] GPIO25
     GPIO11 [23]  | o    o |  [24] GPIO8
        GND [25]  | o    o |  [26] GPIO7
      GPIO0 [27]  | o    o |  [28] GPIO1
      GPIO5 [29]  | o    o |  [30] GND
      GPIO6 [31]  | o    o |  [32] GPIO12 (Repeat LED)*
     GPIO13 [33]  | o    o |  [34] GND
     GPIO19 [35]  | o    o |  [36] GPIO16 (Consume LED)*
     GPIO26 [37]  | o    o |  [38] GPIO20 (Button)
        GND [39]  | o    o |  [40] GPIO21 (Copy LED)
                  +--------+

* Hardware PWM enabled pins
```
> **Important Warning**: GPIO pins 18 and 19 conflict with I2S audio output. While these pins can be changed in the configuration, doing so will affect PWM functionality. If you change these pins, LED dimming (brightness control) through software is not recommended.

## Hardware Components

### TM1637 Display
- **Connections**:
  - CLK: GPIO 15
  - DIO: GPIO 14
  - VCC: 3.3V
  - GND: GND
- **Features**:
  - 4-digit 7-segment display
  - Brightness control (0-7)
  - Multiple display modes

### Status LEDs
- **PWM-enabled LEDs**:
  - Repeat mode (GPIO 12)
  - Random mode (GPIO 13)
  - Single mode (GPIO 18)
  - Consume mode (GPIO 19)
- **Standard LED**:
  - Copy status (GPIO 21)

### Control Button
- Main button on GPIO 20
- Functions:
  - Short press: Toggle play/pause
  - Long press: System shutdown
  - Double press: USB copy (when available)

## Project Structure

```
adam-mpd/
├── config/                 # Configuration files
│   └── settings.json      # Main configuration file
│
├── docs/                  # Documentation
│   └── manual.md         # Technical manual
│
├── scripts/              # Utility scripts
│   ├── toggle_scripts/   # Display and playback mode toggles
│   │   ├── toggle_brightness.py
│   │   ├── toggle_display.py
│   │   ├── toggle_consume.sh
│   │   ├── toggle_random.sh
│   │   ├── toggle_repeat.sh
│   │   └── toggle_single.sh
│   ├── music_takeaway.py # USB copy utility
│   ├── roulette.sh      # Random playback
│   ├── roulette_album.sh # Album-based random
│   └── shutdown.sh      # System shutdown
│
├── src/                  # Source code
│   ├── core/            # Core functionality
│   │   ├── config.py    # Configuration management
│   │   └── mpd_client.py # MPD communication
│   │
│   ├── hardware/        # Hardware interfaces
│   │   ├── button/      # Button control
│   │   ├── display/     # TM1637 display driver
│   │   └── led/        # LED control with PWM
│   │
│   ├── service/         # Main services
│   │   ├── player_service.py    # Main player logic
│   │   └── usb_copy_service.py  # USB operations
│   │
│   ├── utils/           # Utilities
│   │   ├── logger.py    # Logging system
│   │   └── storage.py   # Storage operations
│   │
│   └── main.py          # Application entry point
│
├── .gitignore           # Git ignore rules
├── fix_permissions.sh   # Permission fixing script
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
└── setup.py           # Installation script
```

### Module Descriptions

#### Core (`src/core/`)
- `config.py`: Configuration management with real-time updates
- `mpd_client.py`: MPD client wrapper with connection handling

#### Hardware (`src/hardware/`)
- `button/`: Button controller with multi-function support
- `display/`: TM1637 LED display driver implementation
- `led/`: PWM-enabled LED controller for status indicators

#### Service (`src/service/`)
- `player_service.py`: Main service orchestrating display, LEDs, and MPD
- `usb_copy_service.py`: Handles USB detection and music copying

#### Utils (`src/utils/`)
- `logger.py`: Centralized logging system
- `storage.py`: USB storage operations and file management

#### Scripts (`scripts/`)
- `toggle_scripts/`: User interface control scripts
- `music_takeaway.py`: USB copy utility
- `roulette.sh`: Random playback scripts
- `shutdown.sh`: System shutdown handler

#### Configuration (`config/`)
- `settings.json`: Centralized configuration for all components

## Configuration Reference

### MPD Connection
```json
"mpd": {
    "host": "localhost",  // MPD server address
    "port": 6600         // MPD server port
}
```
Controls the connection to the MPD server. Used by `MPDClient` in `src/core/mpd_client.py`.

### GPIO Settings
```json
"gpio": {
    "button": 20,        // Main control button
    "display": {
        "clk": 15,       // TM1637 clock pin
        "dio": 14        // TM1637 data pin
    },
    "leds": {
        "repeat": 12,    // Repeat mode LED (PWM)
        "random": 13,    // Random mode LED (PWM)
        "single": 18,    // Single mode LED (PWM)
        "consume": 19,   // Consume mode LED (PWM)
        "pwm": {
            "frequency": 1000,           // PWM frequency in Hz
            "pins": [12, 13, 18, 19]    // PWM-enabled pins
        }
    },
    "encoder": {
        "enabled": false,     // Enable/disable encoder support
        "pin_a": 23,         // Encoder pin A
        "pin_b": 24,         // Encoder pin B
        "poll_interval": 100, // Polling rate in ms
        "speed_factor": 2,    // Rotation sensitivity
        "volume_step": 3      // Volume change per step
    }
}
```
Used by hardware controllers in `src/hardware/`. Note the PWM pins configuration for LED brightness control.

### Display Settings
```json
"display": {
    "brightness": 4,    // Default brightness level (0-7)
    "brightness_levels": {
        "led": [25, 50, 100],    // LED brightness percentages
        "display": [2, 4, 7]      // TM1637 brightness levels
    },
    "mode": "elapsed",           // Time display mode (elapsed/remaining)
    "pause_mode": {
        "blink_interval": 1      // Display blink rate when paused
    },
    "play_mode": {
        "track_number_time": 2   // How long to show track number
    },
    "stop_mode": {
        "stop_symbol_time": 2,    // Duration of stop symbol
        "track_total_time": 2,    // Duration of track count
        "total_time_display": 2   // Duration of total time
    }
}
```
Controls display behavior in `src/hardware/display/tm1637.py` and `src/service/player_service.py`.

### Timing Configuration
```json
"timing": {
    "command_cooldown": 1,    // Delay between commands
    "long_press_time": 2,     // Time for long press detection
    "update_interval": 1,     // Display refresh rate
    "volume_display_duration": 3  // How long volume shows
}
```
Used throughout the system for timing control, especially in `PlayerService`.

### USB Copy Settings
```json
"copy": {
    "led": 21,               // Copy status LED pin
    "min_usb_size_gb": 4,    // Minimum USB drive size
    "destination_skip_folders": [  // Folders to ignore
        "NAS",
        "Music",
        "Metal"
    ],
    "path_structure": {
        "min_depth": 4,           // Minimum folder depth
        "artist_level": 2,        // Artist folder position
        "album_level": 3,         // Album folder position
        "music_root": "/var/lib/mpd/music",  // MPD music directory
        "preserve_levels": [2, 3, 4]         // Folder levels to keep
    }
}
```
Controls USB copy functionality in `src/service/usb_copy_service.py`.

### Update Trigger
```json
"updates": {
    "trigger": {
        "file": ".update_trigger",    // Update trigger file
        "check_interval": 1,          // Check frequency
        "debounce_time": 0.1         // Update debounce time
    }
}
```
Used by `PlayerService` for real-time configuration updates.

### Logging
```json
"logging": {
    "enable": true,                // Enable/disable logging
    "level": "DEBUG",             // Log level
    "format": "[{level}] {message}"  // Log message format
}
```
Controls logging behavior in `src/utils/logger.py`.

## Features & Usage

### USB Music Copy (music_takeaway.py)
```bash
# Copy current playing album to USB
./scripts/music_takeaway.py

# Options:
#  --dry-run    Test run without copying
#  --verbose    Show detailed progress
```

### Display Controls
```bash
# Toggle display brightness
./scripts/toggle_scripts/toggle_brightness.py

# Change display mode
./scripts/toggle_scripts/toggle_display.py
```

## Installation Guide

### 1. System Requirements
- Raspberry Pi (3B+ or 4B recommended)
- moOde audio player 8.3.9 or higher
- Python 3.7 or higher
- Git
- Internet connection for package installation

### 2. Base System Setup
```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install required system packages
sudo apt install -y \
    python3-pip \
    python3-venv \
    git
```

### 3. Enable Required Interfaces
1. Enable GPIO:
```bash
sudo raspi-config
# Navigate to: Interface Options
# Enable: GPIO
# Reboot when prompted
```

### 4. Project Installation

#### 4.1. Clone Repository
```bash
# Clone the repository
cd /home/pi
git clone https://github.com/yourusername/adam-mpd.git adam
cd adam

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
```

#### 4.2. Install Dependencies
```bash
# Install Python packages
pip install -e .

# Verify installations
pip list | grep -E "python-mpd2|gpiozero|lgpio|psutil"
```

#### 4.3. Configure Permissions
```bash
# Make scripts executable
sudo chmod +x fix_permissions.sh
sudo ./fix_permissions.sh
```

### 5. Configuration Setup

#### 5.1. Basic Configuration
```bash
# Copy example configuration
cp config/settings.example.json config/settings.json

# Edit configuration
nano config/settings.json
```

#### 5.2. Important Settings to Review
- MPD connection details
- GPIO pin assignments
- Display brightness levels
- Button timing parameters

### 6. Service Installation

#### 6.1. Create Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/adam.service
```

Add the following content:
```ini
[Unit]
Description=Adam for MPD
After=mpd.service
Wants=mpd.service

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/adam
Environment=PYTHONPATH=/home/pi/adam
ExecStart=/home/pi/adam/venv/bin/python3 src/main.py
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=adam

[Install]
WantedBy=multi-user.target
```

#### 6.2. Enable and Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable adam

# Start service
sudo systemctl start adam

# Check status
sudo systemctl status adam
```

### 7. Verify Installation

#### 7.1. Check Service Status
```bash
# View service logs
journalctl -u adam -f

# Check if service is running
systemctl is-active adam
```

#### 7.2. Test Hardware
1. Display should show "--:--"
2. LEDs should reflect MPD status
3. Button should respond to presses

### 8. Troubleshooting

#### 8.1. Permission Issues
```bash
# Re-run permissions script
sudo ./fix_permissions.sh

# Verify user permissions
ls -l /dev/i2c*
ls -l /dev/gpiomem
```

#### 8.2. Service Issues
```bash
# Check detailed service status
sudo systemctl status adam -l

# Check system logs
sudo journalctl -u adam -n 50 --no-pager
```

#### 8.3. Hardware Issues
```bash
# Test GPIO access
gpio readall

# Test display pins
# GPIO 14 (DIO) and GPIO 15 (CLK) should be available
```

### 9. Updates and Maintenance

#### 9.1. Updating the Software
```bash
# Stop service
sudo systemctl stop adam

# Update repository
cd /home/pi/adam
git pull

# Update dependencies
source venv/bin/activate
pip install -e .

# Restart service
sudo systemctl start adam
```

#### 9.2. Backup Configuration
```bash
# Backup settings
cp config/settings.json config/settings.backup.json

# Backup service file
sudo cp /etc/systemd/system/adam.service adam.service.backup
```

For additional support or bug reports, please visit the project's GitHub repository.

## License
This project is free to use and modify. Feel free to tinker and tailor it to your setup.

## Acknowledgments
- [moOde audio player](https://moodeaudio.org/)  
- [MPD (Music Player Daemon)](https://www.musicpd.org/)  
- [TM1637 Datasheet](https://www.makerguides.com/wp-content/uploads/2019/08/TM1637-Datasheet.pdf)

## Support
Got an issue or a feature request? Drop it in this repository’s GitHub issue tracker.
