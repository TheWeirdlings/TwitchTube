'''Creates a Twitch message from another chat'''
import datetime
import json
import redis

import config
REDIS = redis.from_url(config.redisURL)

class TwitchMessageModel(object):
    '''Creates a Twitch message from another chat'''
    def __init__(self, author, text, youtube_id, bot, add_from_youtube=True):
        self.message = ""

        options_exist = "options" in bot
        if options_exist:
            options = bot['options']
        display_exist = options_exist and "displayFromMessages" in options
        display_from_messages_disabled = display_exist and options['displayFromMessages'] is False

        if display_from_messages_disabled:
            add_from_youtube = False

        if add_from_youtube:
            self.message += "(From YouTube) "

        self.message += author + ": " + text

        self.youtube_id = youtube_id
        self.author = author
        self.bot = bot
        self.bot_id = str(self.bot['_id'])

    def save(self):
        '''Saves the message to Redis'''
        time = datetime.datetime.utcnow()

        chat = {
            "bot_id": self.bot_id,
            "message": self.message,
            "sent": False,
            "youtubeId": self.youtube_id,
            "author": self.author,
            "date": time.isoformat(),
            "fromService": "twitch",
        }

        # @TODO: Ensure this is added to the back
        REDIS.lpush("TwitchMessageToSync", json.dumps(chat))
