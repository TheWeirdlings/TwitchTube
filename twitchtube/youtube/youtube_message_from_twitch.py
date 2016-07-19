from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
import config
import datetime
db = client[config.database]
mongoChat = db.twitchMessages
from bson.objectid import ObjectId

class YouTubeMessageFromTwitch(object):
    def __init__(self, bot):
        self.botId = bot

    def getNextMessageToSend(self):
        self.mongoDocument = mongoChat.find_one({
            "sent": False, "bot_id": ObjectId(self.botId),
            "date": {
                "$gt": datetime.datetime.now() - datetime.timedelta(minutes=3)
            },
        })

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
