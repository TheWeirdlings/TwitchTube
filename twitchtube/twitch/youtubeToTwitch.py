import socket, string
from time import sleep
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import twitchConfig

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

client = MongoClient('mongodb://localhost:27017/')
import config
db = client[config.database]
mongoYTChat = db.youtubeMessages

class TwitchMessageFromYouTube(object):
    def __init__(self, bot):
        self.bot = bot

    def getNextMessageToSend(self):
        self.mongoDocument = mongoYTChat.find_one({"sent": False, "bot_id": self.bot['_id']})

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


class YouTubeToTwitch(object):
    def __init__(self, inSocket, run_event, bot):
        self.CHANNEL = '#' + bot['twitch']
        self.s = inSocket
        self.run_event = run_event
        self.bot = bot
        self.setUpTimers()

    def setUpTimers(self):
        timers = db.timers.find({"botId": str(ObjectId(self.bot['_id'])) })

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
            if currentMinute == 0:
                currentMinute = 60
            if currentMinute in self.timers:
                for timerMessage in self.timers[currentMinute]:
                    self.sendTwitchMessge(timerMessage)

    def sendTwitchMessge(self, message):
        try:
            self.s.send("PRIVMSG " + self.CHANNEL + " :" + message + "\r\n")
        except UnicodeDecodeError:
            print 'Add support'

    def sendYoutubeChatToTwitch(self):
        while self.run_event.is_set():
            prevMessage = ""
            chatToSend = TwitchMessageFromYouTube(self.bot)
            chatToSend.getNextMessageToSend()

            self.sendTimers()

            if chatToSend.mongoDocument is not None:
                if ("(From Twitch)" in chatToSend.mongoDocument['message']) or (chatToSend.mongoDocument['message'] == prevMessage):
                    chatToSend.markSent();
                    prevMessage = ""
                else:
                    prevMessage = chatToSend.mongoDocument['message']
                    self.sendTwitchMessge(chatToSend.mongoDocument['message'])
                    chatToSend.markSent();
            sleep(1.5)
