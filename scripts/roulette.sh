#!/bin/bash
echo "[INFO] Starting random mode..."
sudo pkill -f ashuffle
mpc clear
mpc consume on
ashuffle &
echo "[OK] Random mode activated"
