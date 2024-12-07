import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from service.player_service import PlayerService

def main():
    service = PlayerService()
    service.start()

if __name__ == "__main__":
    main()
