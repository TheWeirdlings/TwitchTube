'''A model of a message to be queue from on channel
    to Youtube'''

import datetime
import json
import redis
import config

class YoutubeMessageModel(object):
    '''A model of a message to be queue from on channel
    to Youtube'''

    def __init__(self, author, text, bot, add_from_twitch=True, useOnlyText=False):
        self.redis = redis.from_url(config.redisURL)

        twitch_from_prefix = "(From Twitch)"

        self.author = author

        options_exist = "options" in bot
        if options_exist:
            options = bot['options']
        display_exist = options_exist and "displayFromMessages" in options
        display_from_messages_disabled = display_exist and options['displayFromMessages'] is False

        if display_from_messages_disabled:
            add_from_twitch = False

        message = ""
        if add_from_twitch:
            message = twitch_from_prefix + " "

        if author and useOnlyText is not True:
            message = message + author + ": "

        self.message = message + text

        self.bot_id = bot['_id']

    def save(self):
        '''Saves the model to the Redis Queue'''

        time = datetime.datetime.utcnow()

        chat = {
            "bot_id": str(self.bot_id),
            "message": self.message,
            "sent": False,
            "author": self.author,
            "date": time.isoformat(),
            "fromService": "youtube",
        }

        self.redis.rpush("YoutubeMessageToSync", json.dumps(chat))
