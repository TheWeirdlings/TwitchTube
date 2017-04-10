from twitchtube.twitch.TwitchChatSenderWorker import TwitchChatSenderWorker

if __name__ == "__main__":
    TWITCH_CHAT_SAVER = TwitchChatSenderWorker()
    TWITCH_CHAT_SAVER.start()
