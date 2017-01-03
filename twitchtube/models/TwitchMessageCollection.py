import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

# @TODO: Move somwehre else?
# import config
# client = MongoClient(config.mongoUrl)
# db = client[config.database]
# mongoChat = db.twitchMessages

import redis
# r = redis.StrictRedis()

import config
r = redis.from_url(config.redisURL)

class TwitchMessageCollection(object):
    def __init__(self, bot):
        self.botId = bot['_id']

    def getNextMessageToSend(self):
        return r.lpop("twtichMessageToSync" + str(self.botId))
        self.mongoDocument = mongoChat.find_one({
            "sent": False, "bot_id": ObjectId(self.botId),
            "date": {
                "$gt": datetime.datetime.now() - datetime.timedelta(minutes=3)
            },
        })
        return self.mongoDocument

    def markSent(self):
        result = mongoChat.update_one(
            {"_id": self.mongoDocument['_id']},
            {
                "$set": {
                    "sent": True
                },
                "$currentDate": {"lastModified": True}
            }
        )

    # @TODO: Can we enforce type of the model?
    def saveChat(self, messageMongoObject):
        mongoChat.insert_one(messageMongoObject)
