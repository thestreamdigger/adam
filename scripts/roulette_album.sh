#!/bin/sh
python3 -c "
from src.utils.logger import Logger
log = Logger()
log.info('Starting album random mode...')
"
sudo pkill -f ashuffle
mpc clear
mpc consume off
ashuffle --group-by album &
python3 -c "
from src.utils.logger import Logger
log = Logger()
log.ok('Album random mode activated')
"
