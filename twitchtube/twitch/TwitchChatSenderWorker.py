'''This class grabs and chats that are queued for twitch and
    send them to the twitch channel associated with the bot'''
from datetime import datetime, timezone
from time import sleep
import json
import socket
import redis

import config
from twitchtube.models.TwitchMessageModel import TwitchMessageModel
from twitchtube.models.TwitchMessageCollection import TwitchMessageCollection
from twitchtube.util.EmojiAssigner import EmojiAssigner

class TwitchChatSenderWorker(object):
    '''This class grabs and chats that are queued for twitch and
    send them to the twitch channel associated with the bot'''
    def __init__(self, channel_offset=0):
        self.subscribers = []
        self.bots = []
        self.bots_by_bot_id = {}
        self.channels = []
        self.channels_string = ''
        self.irc_socket = None
        self.channel_offset = channel_offset
        self.max_channel = 50
        self.redis = redis.from_url(config.redisURL)
        self.twitch_collection = TwitchMessageCollection()
        self.last_update_check = datetime.now(timezone.utc)
        self.emoji_assigner = EmojiAssigner()

    # @TODO: Should be an interface
    def register(self, subscriber):
        '''Allows a subscriber to subscribe to this class'''
        self.subscribers.append(subscriber)

    # @TODO: Should be an interface
    def notifiy_subscribers(self):
        '''Notifies all subscribers to execute'''
        for subscriber in self.subscribers:
            subscriber.execute()

    def send_twitch_messge(self, message, channel):
        '''Sends a message to the specified channel'''
        irc_message = 'PRIVMSG %s :%s\n' % (channel, message)
        self.irc_socket.send(irc_message.encode('utf-8'))

    def send_message_from_queue(self):
        '''Grabs next message on queue and sends it
        to the specified channel'''

        # @TODO re append messages that are not used in this bot range

        chat_to_send = self.twitch_collection.get_next_message_to_send()

        if chat_to_send is None:
            return

        chat_to_send = json.loads(chat_to_send.decode())

        if chat_to_send['author'] is 'Twitchtube':
            return

        message = chat_to_send['message']
        bot_id = str(chat_to_send['bot_id'])

        # Put it back, should make this more effiecient
        if bot_id not in self.bots_by_bot_id:
            author = chat_to_send['author']
            text = chat_to_send['message']
            youtube_id = chat_to_send['youtubeId']
            bot = {
                '_id': chat_to_send['bot_id']
            }
            twitch_message_model = TwitchMessageModel(author, text, youtube_id, bot, False, True)
            twitch_message_model.save()
            return

        channel = self.bots_by_bot_id[bot_id]['twitch']

        bot = self.bots_by_bot_id[bot_id]

        has_twitch_options = 'twitchOptions' in bot
        has_emojis = has_twitch_options and 'assignEmojis' in bot['twitchOptions']
        has_emojis_assign = has_emojis and bot['twitchOptions']['assignEmojis'] is True

        if  has_emojis_assign:
            emoji = self.emoji_assigner.getEmojiForUser(chat_to_send['author'])
            if emoji is not None:
                message = emoji + " " + message

        self.send_twitch_messge(message, "#" + channel)

    def connect_to_channels(self):
        '''Create a socket connection to Twitch IRC with all channels'''
        irc_socket = socket.socket()
        irc_socket.connect((config.HOST, config.PORT))

        irc_pass = "PASS " + config.PASS + "\r\n"
        irc_socket.send(irc_pass.encode('utf-8'))

        irc_nick = "NICK " + config.NICK + "\r\n"
        irc_socket.send(irc_nick.encode('utf-8'))

        # ircUser = 'USER ' + config.NICK + ' 0 * :' + config.USER + '\r\n'
        # irc_socket.send(ircUser.encode('utf-8'))

        irc_send_string = "JOIN " + self.channels_string + " \r\n"
        irc_socket.send(irc_send_string.encode('utf-8'))

        self.irc_socket = irc_socket

    def get_channels(self):
        '''Get all Twitch channels in redis queue'''
        begin_index = self.channel_offset * self.max_channel
        end_index = self.max_channel + (self.channel_offset * self.max_channel) - 1
        self.bots = self.redis.lrange('TwitchtubeBots', begin_index, end_index)
        self.bots_by_bot_id = {}
        self.channels = []

        for bot in self.bots:
            cached_bot = json.loads(bot.decode())
            if cached_bot['active']:
                self.channels.append(cached_bot['twitch'])
                bot_id = str(cached_bot['_id'])
                self.bots_by_bot_id[bot_id] = cached_bot

        self.channels_string = ','.join(self.channels)

    def start(self):
        '''Start the Worker'''
        self.get_channels()
        self.connect_to_channels()

        while True:
            now = datetime.now(timezone.utc)
            seconds_since_last_update = (now - self.last_update_check).total_seconds()

            if seconds_since_last_update >= 10:
                self.get_channels()
                self.last_update_check = now

            self.send_message_from_queue()
            # self.notifySubscribers()
            sleep(1.5)
