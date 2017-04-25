'''This class grabs and chats that are queued for twitch and
    send them to the twitch channel associated with the bot'''
from datetime import datetime, timezone
from time import sleep
import json
import socket
import threading
import sys
import pytz
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
            subscriber.execute(self.bots)

    def send_twitch_messge(self, message, channel):
        '''Sends a message to the specified channel'''
        irc_message = 'PRIVMSG %s :%s\n' % (channel, message)
        try:
            print(message, flush=True)
            print(channel, flush=True)
            self.irc_socket.send(irc_message.encode('utf-8'))
            # readbuffer = socket.recv(1024).decode()
            # print(readbuffer)
        except:
            print("Unexpected error:" + str(sys.exc_info()[0]), flush=True)

    def send_message_from_queue(self):
        '''Grabs next message on queue and sends it
        to the specified channel'''

        chat_to_send = self.twitch_collection.get_next_message_to_send()

        if chat_to_send is None:
            return

        chat_to_send = json.loads(chat_to_send.decode())

        if chat_to_send['author'] is 'Twitchtube':
            return

        message = chat_to_send['message']
        bot_id = str(chat_to_send['bot_id'])

        # Put it back, should make this more effiecient
        # @TODO: if it is not active, we should delete the message
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
            if cached_bot['active'] and 'twitch' in cached_bot:
                self.channels.append(cached_bot['twitch'])
                bot_id = str(cached_bot['_id'])
                self.bots_by_bot_id[bot_id] = cached_bot

        self.channels_string = ','.join(self.channels)

    def parse_line(self, line, socket):
        '''Parses a line from the IRC socket'''
        print(line, flush=True)
        if "PING" in line:
            irc_pong = "PONG %s\r\n" % line[1]
            socket.send(irc_pong.encode('utf-8'))
            return

    def read_socket(self, socket):
        '''Listens to messages coming from the irc socket'''
        now = datetime.now(pytz.UTC)
        current_minute = now.minute
        last_minute_sent = None

        while 1:
            now = datetime.now(pytz.UTC)
            current_minute = now.minute

            if current_minute != last_minute_sent:
                last_minute_sent = current_minute
                print("Pinging", flush=True)
                # @TODO: for now we will ping thehollidayinn to keep the socket alive,
                # for some reasons ping pong does not work
                irc_message = 'PRIVMSG %s :%s\n' % ("#thehollidayinn", "Ping")
                socket.send(irc_message.encode('utf-8'))

        # try:
        #     self.readbuffer = self.readbuffer + socket.recv(1024).decode()
        # except:
        #     return
        # temp = self.readbuffer.split("\n")
        # self.readbuffer = temp.pop()
        #
        # for line in temp:
        #     self.parse_line(line, socket)

    def start(self):
        '''Start the Worker'''
        self.get_channels()
        self.connect_to_channels()

        # @TODO: abstract this, but we must keep the socket open
        thread = threading.Thread(target=self.read_socket, \
            args=(self.irc_socket,))
        thread.daemon = True
        thread.start()

        while True:
            now = datetime.now(timezone.utc)
            seconds_since_last_update = (now - self.last_update_check).total_seconds()

            if seconds_since_last_update >= 10:
                self.get_channels()
                self.last_update_check = now

            self.send_message_from_queue()
            self.notifiy_subscribers()
            sleep(.2)
