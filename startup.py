import os
from game.config import config


def check_outlaws_exists():
    if os.path.exists(r'C:\GOG Games\Outlaws\olwin.exe'):
        return True
    else:
        fp = input("Did not locate Outlaws.\nPlease copy and paste path into prompt\n"
                   ":")

        if os.path.exists(fp):
            with open(r"game\config.py") as cfg:
                a = cfg.read()
                print(a['game-file-path'])
            print(config['game-file-path'])


if __name__ == "__main__":
    check_outlaws_exists()