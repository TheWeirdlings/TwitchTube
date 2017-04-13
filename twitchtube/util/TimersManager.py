'''Creates timed messages that will be
    sent at intervals to the bot'''
import datetime
import json
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
        self.last_minute_checked = None

    def execute(self, bots):
        '''Execute when subscriber is called'''

        for bot in bots:
            loaded_bot = json.loads(bot.decode())
            bot_id = str(loaded_bot['_id'])
            self.create_timers(bot_id)
            self.send_timers(loaded_bot)

    def send_timers(self, bot):
        '''Checks for a timed message and
        returns the message if it is time'''
        now = datetime.datetime.now()
        current_minute = now.minute
        bot_id = str(bot['_id'])

        if current_minute != self.last_minute_checked:
            self.last_minute_checked = current_minute
            if current_minute == 0:
                current_minute = 60
            if current_minute in self.bot_timers[bot_id]:
                for timerMessage in self.bot_timers[bot_id][current_minute]:
                    # @TODO: We need some generic way to send to all chat streams
                    # @TODO: remove from youtube here, since this is from us
                    twitch_message = TwitchMessageModel('', timerMessage, None, bot, False)
                    twitch_message.save()

                    # @TODO Abstract Author to constant
                    youtube_message = YoutubeMessageModel('', timerMessage, bot, False)
                    youtube_message.save()

    def create_timers(self, bot_id):
        '''Sets up timers for a bot'''
        if bot_id in self.bot_timers:
            return

        # @TODO: if bot marked for reset check again
        timers = DATABASE.timers.find({"botId": ObjectId(bot_id)})
        #Timers are in the seciton because we need a program that polls the time
        computed_timers = {}

        for timer in timers:
            base_interval = int(timer['interval'])
            interval = base_interval

            while interval <= 60:
                if interval not in timers:
                    computed_timers[interval] = []
                computed_timers[interval].append(timer['message'])
                interval += base_interval

        self.bot_timers[bot_id] = computed_timers
        timers.rewind()
