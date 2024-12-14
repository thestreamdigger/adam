#!/bin/bash
echo "[DEBUG] Checking repeat state"

repeat_state=$(mpc status | grep -o 'repeat: on\|repeat: off')
if [[ $repeat_state == "repeat: on" ]]; then
    echo "[INFO] Disabling repeat mode"
    mpc repeat off
else
    echo "[INFO] Enabling repeat mode"
    mpc repeat on
fi

echo "[OK] Repeat state updated"
