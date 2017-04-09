from twitchtube.twitch.TwitchChatSaverWorker import TwitchChatSaverWorker

if __name__ == "__main__":
    TWITCH_CHAT_SAVER = TwitchChatSaverWorker()
    TWITCH_CHAT_SAVER.start()
