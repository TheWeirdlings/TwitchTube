'''Creates timed messages that will be
    sent at intervals to the bot'''
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

from twitchtube.models.TwitchMessageModel import TwitchMessageModel
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

import config
MONGO = MongoClient(config.mongoUrl)
DATABASE = MONGO[config.database]

class TimersManager(object):
    '''Creates timed messages that will be
    sent at intervals to the bot'''
    def __init__(self):
        self.bot_timers = {}

    def exectute(self, bot_id):
        '''Execute when subscriber is called'''
        self.create_timers(bot_id)
        self.send_timers(bot_id)

    def send_timers(self, bot_id):
        '''Checks for a timed message and
        returns the message if it is time'''
        now = datetime.datetime.now()
        current_minute = now.minute

        if current_minute != self.lastMinuteCheckedForTimers:
            self.last_minute_checked_for_timers = current_minute
            if current_minute == 0:
                current_minute = 60
            if current_minute in self.timers:
                for timerMessage in self.timers[currentMinute]:
                    # @TODO: We need some generic way to send to all chat streams
                    # @TODO: remove from youtube here, since this is from us
                    messageToSave = TwitchMessageModel('', timerMessage, None, self.bot, False)
                    messageToSave.save()

                    # @TODO Abstract Author to constant
                    commandMessageToSave = YoutubeMessageModel('', timerMessage, self.bot, False)
                    commandMessageToSave.save()

    def create_timers(self, bot_id):
        '''Sets up timers for a bot'''
        if bot_id in self.bot_timers:
            return

        timers = DATABASE.timers.find({"botId": ObjectId(bot_id)})

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
        self.last_minute_checked_for_timers = now.minute
