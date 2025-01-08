# Adam for moOde audio player

## Overview & Background
Adam is a project that blends hardware and software to recreate a CD player-style interface on a Raspberry Pi running moOde audio player—where you can literally watch the seconds tick away as the music plays, see the status lights come alive to indicate different functions, and even check how many tracks are loaded or the total runtime of the current album/playlist. It’s all glowingly presented in the same room where your music is playing, without the need to scroll or unlock screens (like on a tablet or a phone). The setup features a spartan 4-digit 7-segment LED display, five indicator LEDs, and a single multi-function push button—just enough for that straightforward, track-and-time display we all know from traditional CD players.

I started—and still maintain—this project as a hobby while I was learning Python, driven by my interest in digital music and the desire for an audio streaming device that shows time and track info the way I had in mind.

## What Has Been Achieved
Adam has grown along with my coding skills, surpassing the initial goal of a single script driving the TM1637 display. The various toggle scripts now manage key playback modes (random, repeat, single, consume) by lighting up the appropriate LEDs, while the display can easily switch between showing elapsed or remaining time (on the fly), total runtime, or even the number of tracks (stop mode). USB copy operations were also introduced via a dedicated script, and the multi-function button was expanded to handle short and long presses for different controls.

Delivering these features required fine-tuning real-time GPIO interactions and code structure—a process that offered invaluable learning experiences. In essence, Adam now provides the streamlined, no-distractions user experience I originally envisioned.

## Hardware Constraints and Alternatives
Working with GPIO on the Raspberry Pi does bring some limitations. Of its 40 pins, only four support hardware PWM, and two of those are typically used for I2S audio. This can complicate LED dimming if you also want to run a DAC over GPIO. Early on, I decided to use USB Audio output, which guided many of my design choices—like dedicating GPIO18 and GPIO19 to hardware PWM instead of I2S.

While exploring other options, I came across Python-compatible microcontrollers—especially the Raspberry Pi Pico (RP2040)—which are both affordable and flexible for handling PWM. This path would avoid compromising GPIO I2S audio on the Pi.

## Future Development
The hardware side of the project relies on a simple set of elements. One of my main goals was to gain practical experience working directly with GPIO pins. Even so, because of an user-friendly configuration file, it’s entirely possible to adapt the code to different pin layouts—or even port it to another hardware platform.

Recently, I’ve been leaning toward UART connectivity for more universal integration. Nearly all SBC music streamers support USB for both control and data, offering a simpler foundation to build upon while freeing up the Pi’s GPIO for more custom hardware expansions. There’s also a lot of potential in turning Adam’s interface into a dedicated USB peripheral—tools like CircuitPython make that surprisingly straightforward.

For now, development will likely focus on bug fixes or new ideas I pick up when I have time to refactor, while firmly keeping the original Adam hardware design for legacy purposes. Adam is a champion and will keep its rightful place, hopefully inspiring you to embark on your own projects. Building your own audio streaming devices may be challenging, but it’s incredibly rewarding once everything comes together.

## Features

### Visual Interface
- **4-digit LED Display (TM1637)**
  - Track numbers (`-XX-`)
  - Total tracks (`XX--`)
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

### Smart USB Operations
- **Quick Album Copy**
  - USB drive detection
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
5. [Configuration Reference](#configuration-reference)
6. [Features & Usage](#features--usage)
7. [Service Installation](#service-installation)

## Hardware Setup

### Required Components
- Raspberry Pi (tested on Model 4B)
- TM1637 4-digit 7-segment display
- 5x LEDs
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
  - Short press: Toggle roulette mode (random playback)
  - Long press: System shutdown

## Project Structure

```
adam-mpd/
├── config/                               # Configuration files
│   └── settings.json                     # Main configuration file
│
├── docs/                                 # Documentation
│   └── manual.md                         # Technical manual
│
├── scripts/                              # Utility scripts
│   ├── toggle_scripts/                   # Display and playback mode toggles
│   │   ├── toggle_brightness.py
│   │   ├── toggle_display.py
│   │   ├── toggle_consume.sh
│   │   ├── toggle_random.sh
│   │   ├── toggle_repeat.sh
│   │   └── toggle_single.sh
│   ├── music_takeaway.py                 # USB copy utility
│   ├── roulette.sh                       # Random playback
│   ├── roulette_album.sh                 # Album-based random
│   └── shutdown.sh                       # System shutdown
│
├── src/                                  # Source code
│   ├── core/                             # Core functionality
│   │   ├── config.py                     # Configuration management
│   │   └── mpd_client.py                 # MPD communication
│   │
│   ├── hardware/                         # Hardware interfaces
│   │   ├── button/                       # Button control
│   │   ├── display/                      # TM1637 display driver
│   │   └── led/                          # LED control
│   │
│   ├── service/                          # Main services
│   │   ├── player_service.py             # Main player logic
│   │   └── usb_copy_service.py           # USB operations
│   │
│   ├── utils/                            # Utilities
│   │   ├── logger.py                     # Logging system
│   │   └── storage.py                    # Storage operations
│   │
│   └── main.py                           # Application entry point
│
├── .gitignore                            # Git ignore rules
├── fix_permissions.sh                    # Permission fixing script
├── README.md                             # Project documentation
├── requirements.txt                      # Python dependencies
└── setup.py                              # Installation script
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
    "host": "localhost",                  // MPD server address
    "port": 6600                          // MPD server port
}
```
Controls the connection to the MPD server. Used by `MPDClient` in `src/core/mpd_client.py`.

### GPIO Settings
```json
"gpio": {
    "button": 20,                         // Main control button
    "display": {
        "clk": 15,                        // TM1637 clock pin
        "dio": 14                         // TM1637 data pin
    },
    "leds": {
        "repeat": 12,                     // Repeat mode LED (PWM)
        "random": 13,                     // Random mode LED (PWM)
        "single": 18,                     // Single mode LED (PWM)
        "consume": 19,                    // Consume mode LED (PWM)
        "pwm": {
            "frequency": 2000,            // PWM frequency in Hz
            "pins": [12, 13, 18, 19]      // PWM-enabled pins
        }
    },
    "encoder": {
        "enabled": false,                 // Enable/disable encoder support
        "pin_a": 23,                      // Encoder pin A
        "pin_b": 24,                      // Encoder pin B
        "poll_interval": 100,             // Polling rate in ms
        "speed_factor": 2,                // Rotation sensitivity
        "volume_step": 3                  // Volume change per step
    }
}
```
Used by hardware controllers in `src/hardware/`. Note the PWM pins configuration for LED brightness control.

### Display Settings
```json
"display": {
    "brightness": 0,                      // Default brightness level (0-7)
    "brightness_levels": {
        "led": [5, 25, 100],              // LED brightness percentages
        "display": [0, 2, 7]              // TM1637 brightness levels
    },
    "mode": "elapsed",                    // Time display mode (elapsed/remaining)
    "pause_mode": {
        "blink_interval": 1               // Display blink rate when paused
    },
    "play_mode": {
        "track_number": {
            "show_number": true,          // Show track numbers
            "display_time": 2             // How long to show track number
        }
    },
    "stop_mode": {
        "stop_symbol_time": 2,            // Duration of stop symbol
        "track_total_time": 2,            // Duration of track count
        "playlist_time": 2                // Duration of playlist time
    }
}
```
Controls display behavior in `src/hardware/display/tm1637.py` and `src/service/player_service.py`.

### Timing Configuration
```json
"timing": {
    "command_cooldown": 0.5,              // Delay between commands
    "long_press_time": 2,                 // Time for long press detection
    "update_interval": 0.2,               // Display refresh rate
    "volume_display_duration": 3          // How long volume shows
}
```
Used throughout the system for timing control, especially in `PlayerService`.

### USB Copy Settings
```json
"copy": {
    "led": 21,                            // Copy status LED pin
    "min_usb_size_gb": 4,                 // Minimum USB drive size
    "destination_skip_folders": [         // Folders to ignore
        "NAS",
        "Music",
        "Metal"
    ],
    "path_structure": {
        "min_depth": 4,                   // Minimum folder depth
        "music_root": "/var/lib/mpd/music"// MPD music directory
    }
}
```
Controls USB copy functionality in `src/service/usb_copy_service.py`.

### Update Trigger
```json
"updates": {
    "trigger": {
        "file": ".update_trigger",        // Update trigger file
        "check_interval": 1,              // Check frequency
        "debounce_time": 0.1              // Update debounce time
    }
}
```
Used by `PlayerService` for real-time configuration updates.

### Logging
```json
"logging": {
    "enable": true,                       // Enable/disable logging
    "level": "DEBUG",                     // Log level
    "format": "[{level}] {message}"       // Log message format
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
- Raspberry Pi
- moOde audio player 9.2 (tested version
- Internet connection for package installation

> **Note**: This installation uses development mode (`pip install -e .`), which is ideal for DIY projects. 
> This means:
> - The code runs directly from the source files in the project directory
> - You can modify files and see changes without reinstalling
> - Good for tinkering and customizing your setup
> - This is how the project was tested and used

### 2. Project Installation

#### 2.1. Clone Repository
```bash
# Clone the repository
cd /home/pi
git clone https://github.com/yourusername/adam-mpd.git adam
cd adam

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
```

#### 2.2. Install Dependencies
```bash
# Install Python packages
pip install -e .

# Verify installations
pip list | grep -E "python-mpd2|gpiozero|lgpio|psutil"
```

#### 2.3. Configure Permissions
```bash
# Make scripts executable
sudo chmod +x fix_permissions.sh
sudo ./fix_permissions.sh
```

### 3. Configuration Setup

#### 3.1. Basic Configuration
```bash
# Copy example configuration
cp config/settings.example.json config/settings.json

# Edit configuration
nano config/settings.json
```

#### 3.2. Important Settings to Review
- MPD connection details
- GPIO pin assignments
- Display brightness levels
- Button timing parameters

### 4. Service Installation

#### 4.1. Create Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/adam.service
```

An example service configuration file is available at `examples/adam.example.service`. You can copy it directly:
```bash
# Copy example service file
sudo cp examples/adam.example.service /etc/systemd/system/adam.service
```

Or create it manually with the following content:
```ini                                                               
[Unit]
Description=Adam for moOde
After=mpd.service
Requires=mpd.service

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/adam
Environment=PYTHONPATH=/home/pi/adam
Environment=PATH=/home/pi/adam/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/home/pi/adam/venv/bin/python3 src/main.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

> **Note**: The example file includes important additional settings such as `Environment=PATH` and `Environment=PYTHONPATH` which are essential for the service to work correctly with the Python virtual environment.

#### 4.2. Enable and Start Service
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

### 5. Verify Installation

#### 5.1. Check Service Status
```bash
# View service logs
journalctl -u adam -f

# Check if service is running
systemctl is-active adam
```

#### 5.2. Test Hardware
1. Display should show "--:--"
2. LEDs should reflect MPD status
3. Button should respond to presses

### 6. Troubleshooting

#### 6.1. Permission Issues
```bash
# Re-run permissions script
sudo ./fix_permissions.sh
```

#### 6.2. Service Issues
```bash
# Check detailed service status
sudo systemctl status adam -l

# Check system logs
sudo journalctl -u adam -n 50 --no-pager
```

## License
This project is free to use and modify. Feel free to tinker and tailor it to your setup.

## Acknowledgments
- [moOde audio player](https://moodeaudio.org/) - The foundation audio system that makes this project possible
- [MPD](https://www.musicpd.org/) - The robust music server at the core
- [TM1637 Datasheet](https://www.makerguides.com/wp-content/uploads/2019/08/TM1637-Datasheet.pdf) - Essential hardware documentation
- [python-mpd2](https://github.com/Mic92/python-mpd2) - Python interface to MPD
- [gpiozero](https://gpiozero.readthedocs.io/) - Simple interface to GPIO devices
- [lgpio](http://abyz.me.uk/lg/py_lgpio.html) - Linux GPIO interface
- [ashuffle](https://github.com/joshkunz/ashuffle) - MPD random playback utility
- The open source community for inspiration and shared knowledge

## Support
For additional support or bug reports, please visit the project's GitHub repository.
