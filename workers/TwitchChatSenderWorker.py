import click

from twitchtube import TwitchChatSenderWorker
from twitchtube import TimersManager
from twitchtube import FollowerManager
from TwitchPythonApi.twitch_api import TwitchApi

import config
from pymongo import MongoClient
MONGO = MongoClient(config.mongoUrl)
DATABASE = MONGO[config.database]

@click.command()
@click.option('--offset', default='', help='The offset of the bot list.')

def start_save(offset=0):
    if offset is '':
        offset = 0
    offset = int(offset)
    twitch_chat_saver = TwitchChatSenderWorker(offset)

    twitch = TwitchApi()
    follower_manager = FollowerManager(DATABASE, twitch)
    twitch_chat_saver.register(follower_manager)

    timer_manager = TimersManager(platform='twitch')
    twitch_chat_saver.register(timer_manager)

    twitch_chat_saver.start()

if __name__ == "__main__":
    start_save()
