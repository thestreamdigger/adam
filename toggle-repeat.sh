#!/bin/bash
repeat_state=$(mpc status | grep -o 'repeat: on\|repeat: off')
if [[ $repeat_state == "repeat: on" ]]; then
    mpc repeat off
else
    mpc repeat on
fi
