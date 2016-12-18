import sys
from time import sleep
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
import config
db = client[config.database]
mongoChat = db.twitchMessages
from bson.objectid import ObjectId
import datetime

from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel
from twitchtube.models.YoutubeMessageCollection import YoutubeMessageCollection
from youtubelivestreaming import live_messages

class YoutubeChatSender(object):
    def __init__(self, bot, youtubeAuth):
        self.subscribers = []

        self.botId = bot['_id']
        self.ytChatModel = YoutubeMessageCollection(bot)
        self.livechat_id = bot['youtube']
        self.youtubeAuth = youtubeAuth
        self.setUpTimers()

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def notifiySubscribers(self):
        for subscriber in self.subscribers:
            subscriber.execute();

    def sendNextTwitchChatToYoutube(self):
        self.ytChatModel.getNextMessageToSend()
        chatToSend = self.ytChatModel.mongoDocument

        if chatToSend is not None:
            self.ytChatModel.markSent()
            try:
                live_messages.insert_message(self.youtubeAuth, self.livechat_id, chatToSend['message'])
            except:
                e = sys.exc_info()[0]
                print("Error: %s" % e)

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
            # self.notifiySubscribers()
            # self.sendTimers()
            self.sendNextTwitchChatToYoutube()
            sleep(1)
