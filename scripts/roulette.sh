#!/bin/bash
sudo pkill -f ashuffle
mpc clear
mpc consume on
ashuffle &
