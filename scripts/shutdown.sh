#!/bin/bash
python3 -c "
from src.utils.logger import Logger
log = Logger()
log.info('Starting shutdown process...')
"

python3 -c "
from src.utils.logger import Logger
log = Logger()
log.wait('Stopping playback...')
"
mpc stop
sleep 0.2

python3 -c "
from src.utils.logger import Logger
log = Logger()
log.wait('Shutting down system...')
"
sudo systemctl poweroff
