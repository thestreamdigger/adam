#!/bin/bash

SERVICE="adam.service"

check_service_status() {
    sudo systemctl is-active --quiet "$1"
    return $?
}

check_service_status "$SERVICE"
SERVICE_STATUS=$?

if [ $SERVICE_STATUS -eq 0 ]; then
    sudo systemctl stop "$SERVICE"
    echo "Service stopped."
else
    sudo systemctl start "$SERVICE"
    echo "Service started."
fi
