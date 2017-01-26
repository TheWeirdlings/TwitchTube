import datetime
from dateutil import parser
import pytz
import json

from twitchtube.models.TwitchMessageModel import TwitchMessageModel
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

class FollowerManager(object):
    def __init__(self, bot, db, twitchApi):
        self.db = db
        self.bot = bot
        self.botId = bot['_id']
        self.twitchApi = twitchApi

        self.lastMinuteCheckedForFollowers = None
        self.lastTimeFollowerAlerted = datetime.datetime.now(pytz.UTC)
        self.twitchChannel = self.bot['twitch']
        self.twitchFollowerCursor = None

    def exectute(self):
        if 'twitchOptions' in self.bot and self.bot['twitchOptions']['displayTwitchAlerts'] == True and 'twitchAlertText' in self.bot['twitchOptions']:
            self.checkForNewFollower()

    def checkForNewFollower(self):
        now = datetime.datetime.now(pytz.UTC)
        currentMinute = now.minute

        if self.lastMinuteCheckedForFollowers is None or currentMinute != self.lastMinuteCheckedForFollowers:
            self.lastMinuteCheckedForFollowers = currentMinute

            followers = self.twitchApi.getFollowers(self.twitchChannel, self.twitchFollowerCursor)
            followers = json.loads(followers)

            # if self.lastTimeFollowerAlerted is None:
            #     if len(followers['follows']) > 0:
            #         lastFollower = followers['follows'][0]
            #         lastFollowerDate = parser.parse(lastFollower['created_at'])
            #         self.lastTimeFollowerAlerted = lastFollowerDate
            #     else:
            #         self.lastTimeFollowerAlerted = now

            for follower in followers['follows']:
                followerDate = parser.parse(follower['created_at'])

                if followerDate > self.lastTimeFollowerAlerted:
                    followerDisplayName = follower['user']['display_name']

                    newFollerMessage = self.bot['twitchOptions']['twitchAlertText']
                    newFollerMessage = newFollerMessage.replace("{{userId}}", followerDisplayName)

                    messageToSave = TwitchMessageModel('', newFollerMessage, None, self.bot, False)
                    messageToSave.save()

                lastFollower = followers['follows'][0]
                lastFollowerDate = parser.parse(lastFollower['created_at'])
                self.lastTimeFollowerAlerted = lastFollowerDate
