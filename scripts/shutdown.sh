#!/bin/bash
echo "[INFO]   Starting shutdown process..."
echo "[WAIT]   Stopping playback..."
mpc stop
sleep 0.2
echo "[WAIT]   Shutting down system..."
sudo systemctl poweroff
