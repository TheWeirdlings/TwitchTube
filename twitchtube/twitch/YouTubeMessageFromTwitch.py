import datetime

class YouTubeMessageFromTwitch(object):
    def __init__(self, author, text, addFromTwitch = True):
        twitchFromPrefix = "(From Twitch)"

        message = ""
        if (addFromTwitch):
            message = twitchFromPrefix + " "

        if (author):
            message = message + author + ": "

        self.message = message + text


    def toMongoObject(self, bot):
        # @TODO: Should we really pass the bot around this way?
        mongoMessage = {
            "bot_id": bot['_id'],
            "message": self.message,
            "sent": False,
            "date": datetime.datetime.utcnow()
        }
        return mongoMessage
