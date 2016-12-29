import cgi
import string
from time import sleep
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

import config
from twitchtube.util.MLStripper import strip_tags
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel
from twitchtube.util.CommandManager import CommandManager

class TwitchChatSaver(object):
    def __init__(self, incSocket, bot, db):
        self.readbuffer = ""
        self.MOTD = False
        self.CHANNEL = "#" + bot['twitch']
        self.s = incSocket
        self.bot = bot
        self.commandManager = CommandManager(db, bot)

    def sendTwitchMessge(self, message):
        ircMessage = 'PRIVMSG %s :%s\n' % (self.CHANNEL, message)
        self.s.send(ircMessage.encode('utf-8'))

    def parseLine(self, line):
        youtubeMessage = ""
        # Checks whether the message is PING because its a method of Twitch to check if you're afk
        if ("PING" in line):
            ircPong = "PONG %s\r\n" % line[1]
            self.s.send(ircPong.encode('utf-8'))
        else:
            parts = line.split(":", 2)
            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                try:
                    # Sets the message variable to the actual message sent
                    message = parts[2][:len(parts[2]) - 1]
                except:
                    message = ""

                # Sets the username variable to the actual username
                usernamesplit = parts[1].split("!")
                username = usernamesplit[0]

                # Only works after twitch is done announcing stuff (MODT = Message of the day)
                if self.MOTD:
                    if (len(message) > 200 or len(message) < 1):
                        return

                    message = strip_tags(message)
                    message = cgi.escape(message)
                    if message is None:
                        return

                    youtubeMessage = YoutubeMessageModel(username, message, self.bot)
                    youtubeMessage.save()

                    commandMessage = self.commandManager.checkForCommands(message, username)
                    if commandMessage is None:
                        return

                    # @TODO: Should we queue up a message instead?
                    self.sendTwitchMessge(commandMessage)


                for l in parts:
                    if "End of /NAMES list" in l:
                        self.MOTD = True

    def readSocket(self):
        self.readbuffer = self.readbuffer + self.s.recv(1024).decode()
        temp = self.readbuffer.split("\n")
        self.readbuffer = temp.pop()

        for line in temp:
            self.parseLine(line)

    def start(self, run_event):
        while run_event.is_set():
            self.readSocket()
            sleep(1.0 / (100.0/30.0))
