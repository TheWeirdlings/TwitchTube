import datetime
from bson.objectid import ObjectId
import json

import redis
r = redis.StrictRedis()

class TwitchMessageModel(object):
    def __init__(self, author, text, youtubeId, botId, addFromYoutube=True):
        self.message = "";
        if (addFromYoutube):
            self.message += "(From YouTube) "
        self.message += author + ": " + text

        self.youtubeId = youtubeId
        self.author = author
        self.botId = botId

    def getMessage(self):
        return self.message

    def toMongoObject(self):
        # @TODO: We need to give this an id for this youtubeToTwitch
        # We don't want to be sending youtube messages from all people
        mongoMessage = {
            "bot_id": ObjectId(self.botId),
            "message": self.message,
            "youtubeId": self.youtubeId,
            "author": self.author,
            "sent": False,
            "date": datetime.datetime.utcnow()
        }
        return mongoMessage #For bulk { '$set': mongoMessage }

    def save(self):
        time = datetime.datetime.utcnow()

        chat = {
            "bot_id": str(self.botId),
            "message": self.message,
            "sent": False,
            "youtubeId": self.youtubeId,
            "author": self.author,
            "date": time.isoformat(),
            "fromService": "twitch",
        }

        r.lpush("twtichMessageToSync" + str(self.botId), json.dumps(chat))
