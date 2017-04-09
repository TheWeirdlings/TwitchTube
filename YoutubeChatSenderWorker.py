from twitchtube.youtube.YoutubeChatSenderWorker import YoutubeChatSenderWorker
from helpers import get_authenticated_service
from oauth2client.tools import argparser

if __name__ == "__main__":

    args = argparser.parse_args()
    youtube = get_authenticated_service(args)

    YOUTUBE_CHAT_SENDER = YoutubeChatSenderWorker(youtube)
    YOUTUBE_CHAT_SENDER.start()
