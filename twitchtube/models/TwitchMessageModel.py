import datetime
from bson.objectid import ObjectId

class TwitchMessageModel(object):
    def __init__(self, author, text, youtubeId, botId):
        self.message = "(From YouTube) " + author + ": " + text
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
