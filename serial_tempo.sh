#!/bin/bash

PYTHON_SCRIPT="/home/pi/serial_tempo.py"
PYTHON_PROCESS="python3 $PYTHON_SCRIPT"

check_process_status() {
    pgrep -f "$PYTHON_PROCESS" > /dev/null
    return $?
}

check_process_status
PROCESS_STATUS=$?

if [ $PROCESS_STATUS -eq 0 ]; then
    sudo pkill -f "$PYTHON_PROCESS"
    echo "serial_tempo script stopped."
else
    sudo python3 "$PYTHON_SCRIPT" &
    echo "serial_tempo script started."
fi
