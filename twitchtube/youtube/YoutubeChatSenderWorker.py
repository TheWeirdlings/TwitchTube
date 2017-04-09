'''Reads messages queue on the Redis server and sends to
the correct Youtube channel'''
import sys
from time import sleep
import json
import redis
from bson.objectid import ObjectId

import config
from twitchtube.models.YoutubeMessageCollection import YoutubeMessageCollection
from youtubelivestreaming import live_messages

class YoutubeChatSenderWorker(object):
    '''Reads messages queue on the Redis server and sends to
    the correct Youtube channel'''
    def __init__(self, youtube_auth):
        self.subscribers = []
        self.youtube_message_collection = YoutubeMessageCollection()
        self.youtube_auth = youtube_auth
        self.bots_hashed_by_id = {}
        self.channel_offset = 0
        self.redis = redis.from_url(config.redisURL)
        self.bots = []

    # @TODO: Should be an interface
    def register(self, subscriber):
        '''Allows a subscriber to subscribe to this class'''
        self.subscribers.append(subscriber)

    # @TODO: Should be an interface
    def notifiy_subscribers(self):
        '''Notifies all subscribers to execute'''
        for subscriber in self.subscribers:
            subscriber.execute()

    def send_next_message(self):
        '''Sends the next message from the Redis queue to Youtube'''
        chat_to_send = self.youtube_message_collection.get_next_message_to_send()

        if chat_to_send is None:
            return

        chat_to_send = json.loads(chat_to_send.decode())

        if 'bot_id' not in chat_to_send:
            return

        bot_id = chat_to_send['bot_id']

        if bot_id not in self.bots_hashed_by_id:
            return

        livechat_id = self.bots_hashed_by_id[bot_id]['youtube']

        try:
            live_messages.insert_message(self.youtube_auth, livechat_id, chat_to_send['message'])
        except:
            print("Unexpected error:" + sys.exc_info()[0], flush=True)

    def get_bots(self):
        '''Gets active bots from redis and creates a hash so we can access
        their live chat ids'''
        begin_index = self.channel_offset * 50
        end_index = self.channel_offset * 50 - 1
        self.bots = self.redis.lrange('TwitchtubeBots', begin_index, end_index)

        for bot in self.bots:
            if 'youtube' in bot:
                self.bots_hashed_by_id[str(bot['_id'])] = {
                    'youtube': bot['youtube']
                }

        self.bots_hashed_by_id['58649647731dd118dc3c0b72'] = {
            'youtube': "EiEKGFVDYzZrWmItSzZJdnBvaEl5SWJMLVZRQRIFL2xpdmU"
        }

    def start(self):
        '''Starts the worker and keeps it running'''

        # @TODO: Add offset acceptor
        self.get_bots()

        while True:
            # self.notifiy_subscribers()
            self.send_next_message()
            sleep(1)
