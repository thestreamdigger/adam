#!/bin/bash

# Define base directory of the project
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[INFO]   Setting up Adam project permissions..."

# Verify if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "[ERROR]  Please run as root or with sudo"
    exit 1
fi

# Set owner and group for all files
echo "[INFO]   Setting owner and group..."
chown -R pi:pi "$BASE_DIR"

# Set directory permissions
echo "[INFO]   Setting directory permissions..."
find "$BASE_DIR" -type d -exec chmod 755 {} \;

# Set Python files permissions
echo "[INFO]   Setting Python files permissions..."
find "$BASE_DIR" -type f -name "*.py" -exec chmod 644 {} \;

# Set executable scripts permissions
echo "[INFO]   Setting script permissions..."
for script in \
    "$BASE_DIR/scripts/adam_go.py" \
    "$BASE_DIR/scripts/roulette.sh" \
    "$BASE_DIR/scripts/roulette_album.sh" \
    "$BASE_DIR/scripts/shutdown.sh"
do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "[OK]     Set executable: $(basename "$script")"
    else
        echo "[WARN]   File not found: $(basename "$script")"
    fi
done

# Set toggle scripts permissions
echo "[INFO]   Setting toggle scripts permissions..."
if [ -d "$BASE_DIR/scripts/toggle_scripts" ]; then
    find "$BASE_DIR/scripts/toggle_scripts" -type f -name "*.sh" -exec chmod +x {} \;
    find "$BASE_DIR/scripts/toggle_scripts" -type f -name "*.py" -exec chmod +x {} \;
    echo "[OK]     Toggle scripts permissions set"
else
    echo "[WARN]   Toggle scripts directory not found"
fi

# Set configuration files permissions
echo "[INFO]   Setting configuration files permissions..."
if [ -d "$BASE_DIR/config" ]; then
    chmod 755 "$BASE_DIR/config"
    find "$BASE_DIR/config" -type f -exec chmod 644 {} \;
    echo "[OK]     Configuration files permissions set"
else
    echo "[WARN]   Config directory not found"
fi

# Set specific permissions for main.py
echo "[INFO]   Setting main file permissions..."
if [ -f "$BASE_DIR/src/main.py" ]; then
    chmod 755 "$BASE_DIR/src/main.py"
    echo "[OK]     Main file permissions set"
else
    echo "[WARN]   Main file not found"
fi

# Create log directory if it doesn't exist
echo "[INFO]   Setting up log directory..."
if [ ! -d "$BASE_DIR/logs" ]; then
    mkdir -p "$BASE_DIR/logs"
    chown pi:pi "$BASE_DIR/logs"
    chmod 755 "$BASE_DIR/logs"
    echo "[OK]     Log directory created"
else
    echo "[OK]     Log directory exists"
fi

echo ""
echo "[OK]     Permissions successfully configured!"
echo ""
echo "Permissions summary:"
echo "- Owner/Group: pi:pi"
echo "- Directories: 755 (drwxr-xr-x)"
echo "- Python files: 644 (-rw-r--r--)"
echo "- Executable scripts: 755 (-rwxr-xr-x)"
echo "- Configuration files: 644 (-rw-r--r--)"
echo "- Log directory: 755 (drwxr-xr-x)" 
