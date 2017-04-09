'''Listens to Youtube channels and saves the chat'''
from time import sleep
from datetime import datetime, timezone
from dateutil import parser
import redis

import config
from youtubelivestreaming import live_messages
from twitchtube.models.TwitchMessageModel import TwitchMessageModel
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel
from twitchtube.util.CommandManager import CommandManager

class YoutubeChatSaverWorker(object):
    '''Listens to Youtube channels and saves the chat'''
    def __init__(self, youtube_auth):
        self.redis = redis.from_url(config.redisURL)
        self.youtube_auth = youtube_auth
        self.channel_offset = 0
        self.bots = []
        self.bot_info = {}
        # self.command_manager = CommandManager(db, bot)

    def save(self, messages, bot):
        '''Saves a list of Youtube messages'''
        for message in messages:
            # Don't save chat sent from the bot - these are commands and timers
            # @TODO Abstract Author to constant
            if message['authorDetails']['displayName'] == 'Twitchtube':
                continue

            username = message['authorDetails']['displayName']
            messagecontent = message['snippet']['displayMessage']
            message_to_save = TwitchMessageModel(username, messagecontent, message['id'], bot)

            # Confirm that we have a new message
            message_published_date = message['snippet']['publishedAt']
            message_published_date = parser.parse(message_published_date)

            # Get last synced date for bot
            bot_id = str(bot['_id'])
            last_synced_message_date = self.bot_info[bot_id]['last_synced_message_date']
            if last_synced_message_date is None:
                last_synced_message_date = datetime.now(timezone.utc)
                self.bot_info[bot_id]['last_synced_message_date'] = last_synced_message_date
                # @TODO: Make this a hashed list instead
                redis_stored_sync_date = self.redis.get(bot_id + "-lastSyncedMessageDate")
                if redis_stored_sync_date is not None:
                    last_synced_message_date = parser.parse(redis_stored_sync_date)

            if last_synced_message_date < message_published_date:
                message_to_save.save()

                last_synced_message_date = message_published_date
                self.bot_info[bot_id]['last_synced_message_date'] = last_synced_message_date
                self.redis.set(bot_id + "-lastSyncedMessageDate", last_synced_message_date.isoformat())

                #Check commands
                # command_message = self.command_manager.checkForCommands(messagecontent, username)
                # if command_message is not None:
                #     command_message_to_save = YoutubeMessageModel('', command_message, bot)
                #     command_message_to_save.save()

    def query_chat(self, bot):
        '''Queries chat for a given youtube channel'''

        livechat_id = bot['youtube']
        bot_id = str(bot['_id'])

        if bot_id not in self.bot_info:
            self.bot_info[bot_id] = {
                'next_page_token': None,
                'last_synced_message_date': None
            }

        next_page_token = self.bot_info[bot_id]['next_page_token']

        response = live_messages.list_messages(self.youtube_auth, livechat_id, next_page_token)

        self.bot_info[bot_id]['next_page_token'] = response['nextPageToken']

        polling_interval_in_millis = response['pollingIntervalMillis']
        polling_interval_in_seconds = polling_interval_in_millis/1000
        self.bot_info[bot_id]['polling_interval_millis'] = polling_interval_in_seconds
        self.bot_info[bot_id]['last_polled_time'] = datetime.now(timezone.utc)

        messages = response.get("items", [])

        self.save(messages, bot)

    def get_bots(self):
        '''Gets active bots from redis and creates a hash so we can access
        their live chat ids'''
        begin_index = self.channel_offset * 50
        end_index = self.channel_offset * 50 - 1
        self.bots = self.redis.lrange('TwitchtubeBots', begin_index, end_index)

        # @TODO: filter for active

        self.bots = [
            {
                '_id': '58649647731dd118dc3c0b72',
                'youtube': "EiEKGFVDYzZrWmItSzZJdnBvaEl5SWJMLVZRQRIFL2xpdmU"
            },
        ]

    def start(self):
        '''Starts the worker and keeps it running'''
        self.get_bots()

        while True:
            for bot in self.bots:
                # Check if we are polling too soon
                bot_id = str(bot['_id'])
                if bot_id in self.bot_info and 'polling_interval_millis' in  self.bot_info[bot_id]:
                    last_polled_time = self.bot_info[bot_id]['last_polled_time']
                    polling_interval_in_seconds = self.bot_info[bot_id]['polling_interval_millis']
                    now = datetime.now(timezone.utc)
                    seconds_since_last_polled = (now - last_polled_time).total_seconds()
                    if seconds_since_last_polled < polling_interval_in_seconds:
                        continue

                self.query_chat(bot)
                sleep(1)
