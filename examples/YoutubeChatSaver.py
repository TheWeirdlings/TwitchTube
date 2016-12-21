import socket
from time import sleep
from oauth2client.tools import argparser

# Ugly hack to allow absolute import from the root folder
# whatever its name is. Please forgive the heresy.
# if __name__ == "__main__" and __package__ is None:
from sys import path
from os.path import dirname as dir

path.append(dir(path[0]))
__package__ = "examples"

import config
from twitchtube.youtube.YoutubeChatSaver import YoutubeChatSaver
from helpers import get_authenticated_service

if __name__ == "__main__":
    args = argparser.parse_args()
    youtube2 = get_authenticated_service(args)

    bot = {
        "youtube": "EiEKGFVDYzZrWmItSzZJdnBvaEl5SWJMLVZRQRIFL2xpdmU",
        "_id": "5853c8142b471021fc94b043"
    }

    ytcs = YoutubeChatSaver(bot, youtube2)

    while True:
        ytcs.saveChat()
