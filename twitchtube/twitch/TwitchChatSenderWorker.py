'''This class grabs and chats that are queued for twitch and
    send them to the twitch channel associated with the bot'''

from time import sleep
import json
import socket
import redis

import config
from twitchtube.models.TwitchMessageCollection import TwitchMessageCollection
from twitchtube.util.EmojiAssigner import EmojiAssigner

class TwitchChatSenderWorker(object):
    '''This class grabs and chats that are queued for twitch and
    send them to the twitch channel associated with the bot'''
    def __init__(self):
        self.subscribers = []
        self.bots = []
        self.bots_by_bot_id = {}
        self.channels = []
        self.channels_string = ''
        self.irc_socket = None
        self.channel_offset = 0
        self.redis = redis.from_url(config.redisURL)
        self.twitch_collection = TwitchMessageCollection()

        # self.emoji_assigner = EmojiAssigner(bot)

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
        channel = self.bots_by_bot_id[bot_id]['twitch']

        # if 'twitchOptions' in self.bot and 'assignEmojis' in self.bot['twitchOptions'] and self.bot['twitchOptions']['assignEmojis'] is True:
        #     emoji = self.emojiAssigner.getEmojiForUser(chatToSend['author'])
        #     if emoji is not None:
        #         message = emoji + " " + message

        self.send_twitch_messge(message, channel)

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
        begin_index = self.channel_offset * 50
        end_index = self.channel_offset * 50 - 1
        self.bots = self.redis.lrange('TwitchtubeBots', begin_index, end_index)

        self.channels = ['#thehollidayinn', '#themisterholliday']
        self.bots_by_bot_id['58649647731dd118dc3c0b72'] = {
            '_id': "58649647731dd118dc3c0b72",
            'twitch': '#thehollidayinn'
        }

        for bot in self.bots:
            if bot['active']:
                self.channels.append(bot['twitch'])

        self.channels_string = ','.join(self.channels)

    def start(self):
        '''Start the Worker'''

        # @TODO: Add offset acceptor
        # @TODO: Add check for bots becoming active

        self.get_channels()
        self.connect_to_channels()

        while True:
            self.send_message_from_queue()
            # self.notifySubscribers()
            sleep(1.5)
