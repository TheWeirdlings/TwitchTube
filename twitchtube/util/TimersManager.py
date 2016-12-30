import datetime

from twitchtube.models.TwitchMessageModel import TwitchMessageModel
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

class TimersManager(object):
    def __init__(self, bot, db):
        self.db = db
        self.bot = bot
        self.botId = bot['_id']
        self.setUpTimers()

    def exectute(self):
        self.sendTimers()

    def sendTimers(self):
        now = datetime.datetime.now()
        currentMinute = now.minute

        if currentMinute != self.lastMinuteCheckedForTimers:
            self.lastMinuteCheckedForTimers = currentMinute
            if currentMinute == 0:
                currentMinute = 60
            if currentMinute in self.timers:
                for timerMessage in self.timers[currentMinute]:
                    # @TODO: We need some generic way to send to all chat streams
                    # @TODO: remove from youtube here, since this is from us
                    messageToSave = TwitchMessageModel('', timerMessage, None, self.botId, False)
                    messageToSave.save()

                    # @TODO Abstract Author to constant
                    commandMessageToSave = YoutubeMessageModel('', timerMessage, self.bot, False)
                    commandMessageToSave.save()

    def setUpTimers(self):
        timers = self.db.timers.find({"botId": self.bot['_id']})

        #Timers are in the seciton because we need a program that polls the time
        self.timers = {}

        for timer in timers:
            baseInterval = int(timer['interval'])
            interval = baseInterval

            while interval <= 60:
                if interval not in self.timers:
                    self.timers[interval] = []
                self.timers[interval].append(timer['message'])
                interval += baseInterval

        now = datetime.datetime.now()
        self.lastMinuteCheckedForTimers = now.minute
