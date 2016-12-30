import datetime
import json

import redis
r = redis.StrictRedis()

class YoutubeMessageModel(object):
    def __init__(self, author, text, bot, addFromTwitch = True):
        twitchFromPrefix = "(From Twitch)"

        self.author = author

        message = ""
        if (addFromTwitch):
            message = twitchFromPrefix + " "

        if (author):
            message = message + author + ": "

        self.message = message + text
        self.bot = bot;
        self.botId = self.bot['_id'];


    def toMongoObject(self, bot):
        # @TODO: Should we really pass the bot around this way?
        mongoMessage = {
            "bot_id": self.bot['_id'],
            "message": self.message,
            "sent": False,
            "date": datetime.datetime.utcnow()
        }
        return mongoMessage

    def save(self):
        time = datetime.datetime.utcnow()

        chat = {
            "bot_id": str(self.bot['_id']),
            "message": self.message,
            "sent": False,
            "author": self.author,
            "date": time.isoformat(),
            "fromService": "youtube",
        }

        r.lpush("youtubeMessageToSync" + str(self.botId), json.dumps(chat))
