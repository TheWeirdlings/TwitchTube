'''Quries Twitch to see if a follower has been created'''
import datetime
import json
from dateutil import parser
import pytz

from twitchtube.models.TwitchMessageModel import TwitchMessageModel

class FollowerManager(object):
    '''Quries Twitch to see if a follower has been created'''

    def __init__(self, database, twitch_api):
        self.database = database
        self.twitch_api = twitch_api
        self.bot_info = {}
        self.last_minute_checked = None

    def bot_has_follower_check(self, bot):
        '''Checks if bot has follower check enabled'''
        has_twitch_options = 'twitchOptions' in bot

        has_display_twitch_alerts = has_twitch_options and \
            'displayTwitchAlerts' in bot['twitchOptions']

        twitch_alerts_enabled = has_display_twitch_alerts and \
            bot['twitchOptions']['displayTwitchAlerts']

        has_twitch_alert_text = has_twitch_options and 'twitchAlertText' in bot['twitchOptions']

        return twitch_alerts_enabled and has_twitch_alert_text

    def is_time_to_check(self):
        '''Throttles to only check every minute'''
        now = datetime.datetime.now(pytz.UTC)
        current_minute = now.minute
        return True
        if self.last_minute_checked is None or current_minute != self.last_minute_checked:
            self.last_minute_checked = current_minute
            return True

        return False

    # @TODO: should be an interface
    def execute(self, bots):
        '''The funciton that is execute everytime the subscriber calls'''

        if not self.is_time_to_check():
            return

        for bot in bots:
            # @TODO: We should probably already have this decoded
            loaded_bot = json.loads(bot.decode())
            if self.bot_has_follower_check(loaded_bot):
                self.check_followers(loaded_bot)

    def last_time_follower_alerted(self, bot_id):
        '''Returns the last time a follower was alerted for the
        given bot id'''
        if bot_id not in self.bot_info:
            self.bot_info[bot_id] = datetime.datetime.now(pytz.UTC)
        return self.bot_info[bot_id]

    def check_followers(self, bot):
        '''Checks the Twitch api for new followers'''
        if 'twitch' not in bot:
            return
        bot_id = str(bot['_id'])
        twitch_channel = bot['twitch']
        follower_cursor = None

        try:
            followers = self.twitch_api.getFollowers(twitch_channel, follower_cursor)
            followers = json.loads(followers)
        except:
            return

        for follower in followers['follows']:
            follower_date = parser.parse(follower['created_at'])

            if follower_date > self.last_time_follower_alerted(bot_id):
                follower_display_name = follower['user']['display_name']

                new_follower_message = bot['twitchOptions']['twitchAlertText']
                new_follower_message = new_follower_message.replace("{{userId}}", \
                    follower_display_name)

                message_to_save = TwitchMessageModel('', new_follower_message, None, bot, False)
                message_to_save.save()

                thank_enabled = 'thankNewFollowers' in bot['twitchOptions']
                thank_new_followers = thank_enabled and bot['twitchOptions']['thankNewFollowers']

                if thank_new_followers:
                    thankfollower_message = 'Thanks for following, @' \
                        + follower['user']['display_name'] + '!'
                    message_to_save = TwitchMessageModel('', thankfollower_message, \
                        None, bot, False)
                    message_to_save.save()

            last_follower = followers['follows'][0]
            last_follower_date = parser.parse(last_follower['created_at'])
            if last_follower_date > self.bot_info[bot_id]:
                self.bot_info[bot_id] = last_follower_date
