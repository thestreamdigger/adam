#!/bin/bash
random_state=$(mpc status | grep -o 'random: on\|random: off')
if [[ $random_state == "random: on" ]]; then
    mpc random off
else
    mpc random on
fi
