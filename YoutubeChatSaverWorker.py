from twitchtube.youtube.YoutubeChatSaverWorker import YoutubeChatSaverWorker
from helpers import get_authenticated_service
from oauth2client.tools import argparser

if __name__ == "__main__":
    ARGS = argparser.parse_args()
    YOUTUBE = get_authenticated_service(ARGS)

    YOUTUBE_CHAT_SAVER = YoutubeChatSaverWorker(YOUTUBE)
    YOUTUBE_CHAT_SAVER.start()
