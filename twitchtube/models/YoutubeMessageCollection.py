import datetime
from pymongo import MongoClient

# @TODO: Move somwehre else?
import config
client = MongoClient(config.mongoUrl)
db = client[config.database]
mongoYTChat = db.youtubeMessages

class YoutubeMessageCollection(object):
    def __init__(self, bot):
        self.bot = bot

    # These are more of collection/reposiotry functions
    def getNextMessageToSend(self):
        self.mongoDocument = mongoYTChat.find_one({
            "sent": False, "bot_id": self.bot['_id'],
            "date": {
                "$gt": datetime.datetime.now() - datetime.timedelta(minutes=3)
            },
        })
        return self.mongoDocument

    # @TODO: This should not handle one at a time or this should be move to a single model
    def markSent(self):
        result = mongoYTChat.update_one(
            {"_id": self.mongoDocument['_id']},
            {
                "$set": {
                    "sent": True
                },
                "$currentDate": {"lastModified": True}
            }
        )

    # @TODO: Can we enforce type of the model?
    def saveChat(self, youtubeMessageMongoObject):
        mongoYTChat.insert_one(youtubeMessageMongoObject)
