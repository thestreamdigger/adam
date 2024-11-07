#!/bin/bash
single_state=$(mpc status | grep -o 'single: on\|single: off')
if [[ $single_state == "single: on" ]]; then
    mpc single off
else
    mpc single on
fi
