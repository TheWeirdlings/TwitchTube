'''Creates timed messages that will be
    sent at intervals to the bot'''
from datetime import datetime
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
import redis

from twitchtube.models.TwitchMessageModel import TwitchMessageModel
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

import config
MONGO = MongoClient(config.mongoUrl)
DATABASE = MONGO[config.database]

class TimersManager(object):
    '''Creates timed messages that will be
    sent at intervals to the bot'''
    def __init__(self, platform=None):
        self.bot_timers = {}
        self.last_minute_checked = None
        self.redis = redis.from_url(config.redisURL)
        self.platform = platform

    def get_current_minute():
        now = datetime.now()
        current_minute = now.minute
        return current_minute

    def execute(self, bots):
        '''Execute when subscriber is called'''
        for bot in bots:
            loaded_bot = json.loads(bot.decode())
            self.create_timers(loaded_bot)
            self.send_timers(loaded_bot)

    def send_timers(self, bot):
        '''Checks for a timed message and
        returns the message if it is time'''
        current_minute = self.get_current_minute()
        bot_id = str(bot['_id'])

        if current_minute != self.last_minute_checked:
            self.last_minute_checked = current_minute
            if current_minute == 0:
                current_minute = 60
            if current_minute in self.bot_timers[bot_id]:
                for timerMessage in self.bot_timers[bot_id][current_minute]:
                    # @TODO: We need some generic way to send to all chat streams
                    # @TODO: remove from youtube here, since this is from us
                    if self.platform == 'twitch' or self.platform is None:
                        twitch_message = TwitchMessageModel('', timerMessage, None, bot, False)
                        twitch_message.save()

                    if self.platform == 'youtube' or self.platform is None:
                        # @TODO Abstract Author to constant
                        youtube_message = YoutubeMessageModel('', timerMessage, bot, False)
                        youtube_message.save()

    def create_timers(self, bot):
        '''Sets up timers for a bot'''
        bot_id = str(bot['_id'])
        reset_check = 'reset_check' in bot
        reset_check_commands = reset_check and 'timers' in bot['reset_check'] \
            and bot['reset_check']['timers'] is False
        if bot_id in self.bot_timers and not reset_check_commands:
            return

        if reset_check_commands:
            # @TODO: this will reset for 10 seconds unfortunately
            # because youtube checks for updates every 10 seconds
            # We need a reactive pattern and notfiy rather than query
            bot['reset_check']['timers'] = True
            list_index = bot['list_index']
            self.redis.hmset('TwitchtubeBotsById', {str(bot['_id']): json.dumps(bot)})
            self.redis.lset('TwitchtubeBots', list_index - 1, json.dumps(bot))

        # @TODO: if bot marked for reset check again
        timers = DATABASE.timers.find({
            "botId": ObjectId(bot_id),
            "$or": [
                {"platform": {"$exists": False}},
                {"platform": self.platform},
                {"platform": "all"},
            ]
        })
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
