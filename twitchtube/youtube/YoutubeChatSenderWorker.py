'''Reads messages queue on the Redis server and sends to
the correct Youtube channel'''
import sys
from time import sleep
import json
import redis

import config
from twitchtube.models.YoutubeMessageCollection import YoutubeMessageCollection
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel
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
            subscriber.execute(self.bots)

    def requeue_message(self, chat_to_send):
        '''Adds a message back to the queue'''
        username = chat_to_send['author']
        message = chat_to_send['message']
        bot = {
            '_id': chat_to_send['bot_id']
        }
        youtube_message = YoutubeMessageModel(username, message, bot, False, True)
        youtube_message.save()

    def send_next_message(self):
        '''Sends the next message from the Redis queue to Youtube'''
        chat_to_send = self.youtube_message_collection.get_next_message_to_send()

        if chat_to_send is None:
            return

        chat_to_send = json.loads(chat_to_send.decode())

        if 'bot_id' not in chat_to_send:
            return

        bot_id = chat_to_send['bot_id']

        cached_bot = self.redis.hget('TwitchtubeBotsById', bot_id)
        if cached_bot is None:
            self.requeue_message(chat_to_send)
            return

        cached_bot = json.loads(cached_bot.decode())
        if not cached_bot['active']:
            self.requeue_message(chat_to_send)
            return

        livechat_id = cached_bot['youtube']

        try:
            live_messages.insert_message(self.youtube_auth, livechat_id, chat_to_send['message'])
        except:
            print("Unexpected error:" + str(sys.exc_info()[0]), flush=True)

    def start(self):
        '''Starts the worker and keeps it running'''

        while True:
            self.notifiy_subscribers()
            self.send_next_message()
            sleep(1)
