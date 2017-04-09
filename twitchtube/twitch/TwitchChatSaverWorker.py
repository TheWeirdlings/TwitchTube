'''A worker that connects to Twitch IRC for multiple channels
    and saves the chats in a Redis queue to be processes'''

import socket
import cgi

import config
from twitchtube.util.MLStripper import strip_tags
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel
from twitchtube.util.CommandManager import CommandManager

class TwitchChatSaverWorker(object):
    '''A worker that connects to Twitch IRC for multiple channels
    and saves the chats in a Redis queue to be processes'''

    def __init__(self):
        self.readbuffer = ""
        self.motd = False
        self.motd_count = False #We need to account for each motd for each channel
        self.channels = []
        self.channels_string = ''
        self.bot = {} #bot
        self.database = {}
        # self.command_manager = CommandManager(self.database, self.bot)
        self.channel_offset = 0
        self.irc_socket = None
        self.redis = None

    def send_twitch_method(self, message, channel):
        '''Sends a message to the IRC socket'''
        irc_message = 'PRIVMSG %s :%s\n' % (channel, message)
        self.irc_socket.send(irc_message.encode('utf-8'))

    def parse_line(self, line):
        '''Parses a line from the IRC socket'''

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
        if len(usernamesplit) > 1:
            channelsplit = usernamesplit[1].split('#')
            channel = channelsplit[1].strip()

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

        print(channel, flush=True)
        print(message, flush=True)

        #@TOOD: This should be queue up as any message not just youtube
        # youtube_message = YoutubeMessageModel(username, message, self.bot)
        # youtube_message.save()

        # command_message = self.command_manager.checkForCommands(message, username)
        # if command_message is None:
        #     return

        # @TODO: Should we queue up a message instead?
        # self.send_twitch_method(command_message)

    def read_socket(self):
        '''Listens to messages coming from the irc socket'''
        self.readbuffer = self.readbuffer + self.irc_socket.recv(1024).decode()
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

        # irc_send_string = "JOIN #" + self.bot['twitch'] + " \r\n"
        irc_send_string = "JOIN " + self.channels_string + " \r\n"
        irc_socket.send(irc_send_string.encode('utf-8'))

        self.irc_socket = irc_socket

    def get_channels(self):
        '''Get all Twitch channels in redis queue'''
        begin_index = self.channel_offset * 50
        end_index = self.channel_offset * 50 - 1
        self.channels = ['#thehollidayinn', '#themisterholliday']
        self.channels_string = ','.join(self.channels)
        #self.redis.lrange('twitchChannels', begin_index, end_index)

    def start(self):
        '''Start the Worker'''

        self.get_channels()
        self.connect_to_channels()

        while True:
            self.read_socket()
