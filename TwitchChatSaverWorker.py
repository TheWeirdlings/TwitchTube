import click

from twitchtube.twitch.TwitchChatSaverWorker import TwitchChatSaverWorker

@click.command()
@click.option('--offset', default='', help='The offset of the bot list.')

def start_save(offset=0):
    if offset is '':
        offset = 0
    offset = int(offset)
    twitch_chat_saver = TwitchChatSaverWorker(offset)
    twitch_chat_saver.start()

if __name__ == "__main__":
    start_save()
