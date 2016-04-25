import datetime
from bson.objectid import ObjectId

class TwitchMessageFromYouTube(object):
    def __init__(self, author, text, youtubeId, botId):
        self.message = "(From YouTube) " + author + ": " + text
        self.youtubeId = youtubeId
        self.botId = botId

    def toMongoObject(self):
        # @TODO: We need to give this an id for this youtubeToTwitch
        # We don't want to be sending youtube messages from all people
        mongoMessage = {
            "bot_id": ObjectId(self.botId),
            "message": self.message,
            "youtubeId": self.youtubeId,
            "sent": False,
            "date": datetime.datetime.utcnow()
        }
        return mongoMessage #For bulk { '$set': mongoMessage }
