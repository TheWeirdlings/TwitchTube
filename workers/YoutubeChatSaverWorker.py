import click

from twitchtube import YoutubeChatSaverWorker
from twitchtube import TimersManager
from helpers import get_authenticated_service
from oauth2client.tools import argparser

YOUTUBE = None

@click.command()
@click.option('--offset', default='', help='The offset of the bot list.')

def start_save(offset=0):
    if offset is '':
        offset = 0
    offset = int(offset)
    youtube_chat_saver = YoutubeChatSaverWorker(YOUTUBE, offset)

    timer_manager = TimersManager(platform='youtube')
    youtube_chat_saver.register(timer_manager)

    youtube_chat_saver.start()

if __name__ == "__main__":
    ARGS = argparser.parse_args()
    YOUTUBE = get_authenticated_service(ARGS)
    start_save()
