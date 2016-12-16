import json
import string
from pymongo import MongoClient
import datetime

import config
client = MongoClient(config.mongoUrl)
db = client[config.database]
mongoTwitchUsers = db.youtubeViewers

from youtubelivestreaming.live_broadcasts import get_live_broadcasts_list

class YoutubePointManager(object):
    def __init__(self, youtubeApi):
        self.youtubeApi = youtubeApi
        now = datetime.datetime.now()
        self.lastMinuteCheckedForTimers = now.minute

    #@TODO: Move to Youtube api
    def getYoutubeStats(self):
        print(get_live_broadcasts_list(self.youtubeApi))
        r = requests.get('https://www.youtube.com/live_stats?v=c6kZb-K6IvpohIyIbL-VQA1441139657488068')
        print(r.json())

    def execute(self):
        now = datetime.datetime.now()
        currentMinute = now.minute

        # print db.users.find()
        # print self.getYoutubeStats();

        #Only give points every minute
        # if currentMinute != self.lastMinuteCheckedForTimers:
        #     self.lastMinuteCheckedForTimers = currentMinute

            # print self.getYoutubeStats();
            # viewers = self.twitchApi.getViewers(self.bot['twitch'])
            # viewers = json.loads(viewers)
            # if 'chatters' in viewers and 'viewers' in viewers['chatters']:
            #     self.scoreViewers(viewers['chatters']['viewers'])
            #     print viewers['chatters']['viewers']

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
