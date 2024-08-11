#!/bin/bash
consume_state=$(mpc status | grep -o 'consume: on\|consume: off')
if [[ $consume_state == "consume: on" ]]; then
    mpc consume off
else
    mpc consume on
fi
