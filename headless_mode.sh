#!/bin/bash

SERVICE1="tempo.service"
SERVICE2="led_control.service"

check_service_status() {
    systemctl is-active --quiet "$1"
    return $?
}

check_service_status "$SERVICE1"
SERVICE1_STATUS=$?

check_service_status "$SERVICE2"
SERVICE2_STATUS=$?

if [ $SERVICE1_STATUS -eq 0 ] && [ $SERVICE2_STATUS -eq 0 ]; then
    systemctl stop "$SERVICE1"
    systemctl stop "$SERVICE2"
    echo "Services stopped."
    
elif [ $SERVICE1_STATUS -ne 0 ] && [ $SERVICE2_STATUS -ne 0 ]; then
    systemctl start "$SERVICE1"
    systemctl start "$SERVICE2"
    echo "Services started."

else
    systemctl start "$SERVICE1"
    systemctl start "$SERVICE2"
    echo "Services started."
fi
