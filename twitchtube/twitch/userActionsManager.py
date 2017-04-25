import json
import string
from pymongo import MongoClient
import datetime

from TwitchPythonApi.twitch_api import TwitchApi

client = MongoClient('mongodb://localhost:27017/')
import config
db = client[config.database]
mongoTwitchUsers = db.twitchViewers

class UserActionsManager(object):
    def __init__(self, socket, bot):
        self.socket = socket
        self.bot = bot
        self.twitchApi = TwitchApi()

        now = datetime.datetime.now()
        self.lastMinuteCheckedForTimers = now.minute

    def exectute(self):
        now = datetime.datetime.now()
        currentMinute = now.minute
        #Only give points every minute
        if currentMinute != self.lastMinuteCheckedForTimers:
            self.lastMinuteCheckedForTimers = currentMinute

            viewers = self.twitchApi.getViewers(self.bot['twitch'])
            viewers = json.loads(viewers)
            if 'chatters' in viewers and 'viewers' in viewers['chatters']:
                self.scoreViewers(viewers['chatters']['viewers'])
                print(viewers['chatters']['viewers'])

    def scoreViewers(self, viewers):
        for viewer in viewers:
            foundTwitchUser = mongoTwitchUsers.find_one({"twitchId": viewer})
            if foundTwitchUser is None:
                newTwitchViewer = {
                    "bot_id": self.bot['_id'],
                    "twitchId": viewer,
                    "dateFirstSeen": datetime.datetime.utcnow(),
                    "points": 10,
                }
                mongoTwitchUsers.insert(newTwitchViewer)
            else:
                result = mongoTwitchUsers.update_one(
                    {"_id": foundTwitchUser['_id']},
                    {
                        "$set": {
                            "points": foundTwitchUser['points'] + 10, #User increatement,
                            "dateLastSeen": datetime.datetime.utcnow(),
                        },
                        "$currentDate": {"lastModified": True}
                    }
                )
