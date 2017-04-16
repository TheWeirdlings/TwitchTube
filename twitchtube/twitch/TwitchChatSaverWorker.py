'''A worker that connects to Twitch IRC for multiple channels
    and saves the chats in a Redis queue to be processes'''

import socket
from datetime import datetime, timezone
import cgi
import json
import threading
import redis

import config
from twitchtube.util.MLStripper import strip_tags
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel
from twitchtube.util.CommandManager import CommandManager

class TwitchChatSaverWorker(object):
    '''A worker that connects to Twitch IRC for multiple channels
    and saves the chats in a Redis queue to be processes'''

    def __init__(self, channel_offset=0):
        self.readbuffer = ""
        self.motd = False
        self.motd_count = False #We need to account for each motd for each channel
        self.channels = []
        self.channels_string = ''
        self.bots = []
        self.bots_hashed_by_channel = {}
        self.bot = {} #bot
        self.database = {}
        # @TODO: inject or someone have the need to change code here
        self.command_manager = CommandManager()
        self.channel_offset = channel_offset
        self.max_channel = 50
        self.irc_socket = None
        self.redis = redis.from_url(config.redisURL)
        self.last_update_check = datetime.now(timezone.utc)

    def send_twitch_method(self, message, channel):
        '''Sends a message to the IRC socket'''
        irc_message = 'PRIVMSG %s :%s\n' % (channel, message)
        self.irc_socket.send(irc_message.encode('utf-8'))

    def parse_line(self, line):
        '''Parses a line from the IRC socket'''
        print(line, flush=True)
        if "PING" in line:
            irc_pong = "PONG %s\r\n" % line[1]
            self.irc_socket.send(irc_pong.encode('utf-8'))
            return

        parts = line.split(":", 2)
        if "QUIT" in parts[1] or "JOIN" in parts[1] or "PART" in parts[1]:
            return

        message = parts[2][:len(parts[2]) - 1]

        # Sets the username variable to the actual username
        usernamesplit = parts[1].split("!")
        username = usernamesplit[0]
        channel = None
        if len(usernamesplit) > 1:
            channelsplit = usernamesplit[1].split('#')
            channel = '#' + channelsplit[1].strip()

        # Only works after twitch is done announcing stuff (MODT = Message of the day)
        if self.motd is False:
            for line_item in parts:
                if "End of /NAMES list" in line_item:
                    self.motd_count += 1
                    if self.motd_count is not len(self.channels):
                        continue
                    self.motd = True
            return

        if len(message) > 200 or len(message) < 1:
            return

        message = strip_tags(message)
        message = cgi.escape(message)
        if message is None:
            return

        if channel is None:
            return

        channel_exists = channel in self.bots_hashed_by_channel
        channel_active = channel_exists and self.bots_hashed_by_channel[channel]['active']
        if channel_active is False:
            return

        bot = self.bots_hashed_by_channel[channel]

        # @TODO: abstract twitchtubebot to constant
        # @TODO: This should be queue up as any message not just youtube
        if username != 'twitchtubebot':
            youtube_message = YoutubeMessageModel(username, message, bot)
            youtube_message.save()

        update = False
        reset_check = 'reset_check' in bot
        reset_check_commands = reset_check and 'commands' in bot['reset_check'] \
            and bot['reset_check']['commands'] is False
        if bot['status'] == 'restart' and reset_check_commands:
            update = True
            bot['reset_check']['commands'] = True
            self.bots_hashed_by_channel[channel]['reset_check']['commands'] = True
            list_index = bot['list_index']
            self.redis.hmset('TwitchtubeBotsById', {str(bot['_id']): json.dumps(bot)})
            self.redis.lset('TwitchtubeBots', list_index - 1, json.dumps(bot))

        command_message = self.command_manager.check_for_commands(message, \
            username, str(bot['_id']), update)
        if command_message is None:
            return

        # @TODO: Should we queue up a message instead?
        self.send_twitch_method(command_message, channel)

    def read_socket(self):
        '''Listens to messages coming from the irc socket'''
        try:
            self.readbuffer = self.readbuffer + self.irc_socket.recv(1024).decode()
        except:
            return
        temp = self.readbuffer.split("\n")
        self.readbuffer = temp.pop()

        for line in temp:
            self.parse_line(line)

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

     # @TODO Move to separate class?
    def connect_to_new_channels(self, irc_socket):
        '''Uses existing socket to connect to IRC'''
        irc_send_string = "JOIN " + self.channels_string + " \r\n"
        irc_socket.send(irc_send_string.encode('utf-8'))

    def get_channels(self, bots, bots_hashed_by_channel):
        '''Get all Twitch channels in redis queue'''
        begin_index = self.channel_offset * self.max_channel
        end_index = self.max_channel + (self.channel_offset * self.max_channel) - 1
        bots = self.redis.lrange('TwitchtubeBots', begin_index, end_index)

        channels = []

        for bot in bots:
            bot_parsed = json.loads(bot.decode())
            channel = '#' + bot_parsed['twitch']
            bot_active = bot_parsed['active']

            # if we haven't joined the channel, add it
            channel_doesnt_exist = bot_active and channel not in bots_hashed_by_channel
            if channel_doesnt_exist:
                channels.append(channel)
                bots_hashed_by_channel[channel] = bot_parsed

            # Update full bot if we have already joined
            channel_exists = channel in bots_hashed_by_channel
            channel_became_active = channel_exists and \
                bots_hashed_by_channel[channel]['active'] is False
            channel_became_active = channel_became_active and bot_active
            if channel_became_active:
                bots_hashed_by_channel[channel]['active'] = bot_parsed

            # Channel became inactive
            channel_became_inactive = channel_exists and \
                bots_hashed_by_channel[channel]['active'] is True
            channel_became_inactive = channel_became_inactive and bot_active is False
            if channel_became_inactive:
                bots_hashed_by_channel[channel]['active'] = bot_parsed

            # @TODO: Add a check list for restart conditions
            # @TODO: Abstract to model
            reset_check = 'reset_check' in bot_parsed
            reset_twitchsaver = reset_check and 'twitchsaver' in bot_parsed['reset_check'] \
                and bot_parsed['reset_check']['twitchsaver'] is False
            if bot_parsed['status'] == 'restart' and reset_twitchsaver:
                bots_hashed_by_channel[channel] = bot_parsed
                bots_hashed_by_channel[channel]['reset_check']['twitchsaver'] = True
                list_index = bot_parsed['list_index']
                self.redis.hmset('TwitchtubeBotsById', {str(bot_parsed['_id']): json.dumps(bot_parsed)})
                self.redis.lset('TwitchtubeBots', list_index - 1, json.dumps(bot_parsed))

        self.channels_string = ','.join(channels)

        return channels

    def check_for_updates(self, bots, bots_hashed_by_channel, irc_socket, channels_global, message_of_day):
        '''A function to use a separate thread
        that checks for channel updates'''
        while True:
            now = datetime.now(timezone.utc)
            seconds_since_last_update = (now - self.last_update_check).total_seconds()
            if seconds_since_last_update >= 10:
                channels = self.get_channels(bots, bots_hashed_by_channel)
                if len(channels) > 0:
                    channels_global.extend(channels)
                    message_of_day = False
                    self.connect_to_new_channels(irc_socket)
                self.last_update_check = now

    def start(self):
        '''Start the Worker'''

        channels = self.get_channels(self.bots, self.bots_hashed_by_channel)
        if len(channels) > 0:
            self.channels.extend(channels)
            self.connect_to_channels()

        thread = threading.Thread(target=self.check_for_updates, \
            args=(self.bots, self.bots_hashed_by_channel, self.irc_socket, self.channels, self.motd))
        thread.daemon = True
        thread.start()

        while True:
            self.read_socket()
