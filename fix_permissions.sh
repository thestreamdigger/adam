#!/bin/bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[INFO] Setting up Adam for MPD permissions..."

if [ "$EUID" -ne 0 ]; then 
    echo "[ERROR] Please run as root or with sudo"
    exit 1
fi

echo "[INFO] Setting owner and group..."
chown -R pi:pi "$BASE_DIR"

echo "[INFO] Setting directory permissions..."
find "$BASE_DIR" -type d -exec chmod 755 {} \;

echo "[INFO] Setting Python files permissions..."
find "$BASE_DIR" -type f -name "*.py" -exec chmod 644 {} \;

echo "[INFO] Setting script permissions..."
for script in \
    "$BASE_DIR/scripts/music_takeaway.py" \
    "$BASE_DIR/scripts/roulette.sh" \
    "$BASE_DIR/scripts/roulette_album.sh" \
    "$BASE_DIR/scripts/shutdown.sh"
do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "[OK] Set executable: $(basename "$script")"
    else
        echo "[WARN] File not found: $(basename "$script")"
    fi
done

echo "[INFO] Setting toggle scripts permissions..."
if [ -d "$BASE_DIR/scripts/toggle_scripts" ]; then
    find "$BASE_DIR/scripts/toggle_scripts" -type f -name "*.sh" -exec chmod +x {} \;
    find "$BASE_DIR/scripts/toggle_scripts" -type f -name "*.py" -exec chmod +x {} \;
    echo "[OK] Toggle scripts permissions set"
else
    echo "[WARN] Toggle scripts directory not found"
fi

echo "[INFO] Setting configuration files permissions..."
if [ -d "$BASE_DIR/config" ]; then
    chmod 755 "$BASE_DIR/config"
    find "$BASE_DIR/config" -type f -exec chmod 644 {} \;
    echo "[OK] Configuration files permissions set"
else
    echo "[WARN] Config directory not found"
fi

echo "[INFO] Setting main file permissions..."
if [ -f "$BASE_DIR/src/main.py" ]; then
    chmod 755 "$BASE_DIR/src/main.py"
    echo "[OK] Main file permissions set"
else
    echo "[WARN] Main file not found"
fi

echo "[OK] Permissions successfully configured!"

echo "[INFO] Permissions summary:"
echo "[INFO] - Owner/Group: pi:pi"
echo "[INFO] - Directories: 755 (drwxr-xr-x)"
echo "[INFO] - Python files: 644 (-rw-r--r--)"
echo "[INFO] - Executable scripts: 755 (-rwxr-xr-x)"
echo "[INFO] - Configuration files: 644 (-rw-r--r--)"
echo "[INFO] - Log directory: 755 (drwxr-xr-x)"
