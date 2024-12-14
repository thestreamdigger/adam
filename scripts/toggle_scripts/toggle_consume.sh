#!/bin/bash
echo "[DEBUG] Checking consume state"

consume_state=$(mpc status | grep -o 'consume: on\|consume: off')
if [[ $consume_state == "consume: on" ]]; then
    echo "[INFO] Disabling consume mode"
    mpc consume off
else
    echo "[INFO] Enabling consume mode"
    mpc consume on
fi

echo "[OK] Consume state updated"
