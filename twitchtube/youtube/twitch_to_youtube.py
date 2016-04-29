from time import sleep
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
import config
db = client[config.database]
mongoChat = db.twitchMessages
from bson.objectid import ObjectId
import datetime

from youtube_message_from_twitch import YouTubeMessageFromTwitch
from youtubelivestreaming import live_messages

class TwitchToYouTube(object):
    def __init__(self, bot, youtubeAuth):
        self.botId = bot['_id']
        self.ytChatModel = YouTubeMessageFromTwitch(self.botId)
        self.livechat_id = bot['youtube']
        self.youtubeAuth = youtubeAuth
        self.setUpTimers()

    def sendNextTwitchChatToYoutube(self):
        self.ytChatModel.getNextMessageToSend()
        chatToSend = self.ytChatModel.mongoDocument
        if chatToSend is not None:
            self.ytChatModel.markSent()
            live_messages.insert_message(self.youtubeAuth, self.livechat_id, chatToSend['message'])

    def setUpTimers(self):
        timers = db.timers.find({"botId": str(ObjectId(self.botId))})

        #Timers are in the seciton because we need a program that polls the time
        self.timers = {}

        for timer in timers:
            interval = int(timer['interval'])

            while interval <= 60:
                if interval not in self.timers:
                    self.timers[interval] = []
                self.timers[interval].append(timer['message'])
                interval += interval

        now = datetime.datetime.now()
        self.lastMinuteCheckedForTimers = now.minute

    def sendTimers(self):
        now = datetime.datetime.now()
        currentMinute = now.minute

        if currentMinute != self.lastMinuteCheckedForTimers:
            self.lastMinuteCheckedForTimers = currentMinute
            #We handle every hour as 60, so change 0 to 60 for the hour mark
            if currentMinute == 0:
                currentMinute = 60
            if currentMinute in self.timers:
                for timerMessage in self.timers[currentMinute]:
                    live_messages.insert_message(self.youtubeAuth, self.livechat_id, timerMessage)

    def run(self, run_event):
        while run_event.is_set():
            self.sendTimers()
            self.sendNextTwitchChatToYoutube()
            sleep(1)
