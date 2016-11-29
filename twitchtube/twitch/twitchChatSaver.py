import cgi
import string
from time import sleep
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

import config

client = MongoClient(config.mongoUrl)
db = client[config.database]
bots = db.twitchtubeBots
mongoChat = db.twitchMessages
mongoCommands = db.commands

youtubeFromPrefix = "(From YouTube)"

class TwitchChatSaver(object):

    def __init__(self, incSocket, bot):
        self.readbuffer = ""
        self.MOTD = False
        self.CHANNEL = "#" + bot['twitch']

        self.twitchMessagesToSave = []
        self.s = incSocket

        self.commands = mongoCommands.find({"botId": str(ObjectId(bot['_id'])) })

        self.bot = bot

    def strip_tags(self, html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    def sendTwitchMessge(self, message):
        try:
            self.s.send("PRIVMSG " + self.CHANNEL + " :" + message + "\r\n")
        except UnicodeDecodeError:
            print 'Add support'

    def checkForCommands(self, message, username):
        self.commands = mongoCommands.find({"botId": str(ObjectId(self.bot['_id'])) })
        for command in self.commands:
            if (command['command'] == message and youtubeFromPrefix not in message):
                self.sendTwitchMessge(command['message'])

    def parseLine(self, line):
        youtubeMessage = ""
        # Checks whether the message is PING because its a method of Twitch to check if you're afk
        if ("PING" in line):
            self.s.send("PONG %s\r\n" % line[1])
        else:
            parts = line.split(":", 2)
            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                try:
                    # Sets the message variable to the actual message sent
                    message = parts[2][:len(parts[2]) - 1]
                except:
                    message = ""

                # Sets the username variable to the actual username
                usernamesplit = string.split(parts[1], "!")
                username = usernamesplit[0]

                # Only works after twitch is done announcing stuff (MODT = Message of the day)
                if self.MOTD:
                    #Check if the message was transferred from Youtube.
                    # @TODO: Maybe one day we can have a more sequential syncing?
                    if ("(From YouTube)" in line or len(message) > 200 or len(message) < 1):
                        print "Skip chat"
                    else:
                        message = self.strip_tags(message)
                        message = cgi.escape(message)
                        if message:
                            self.checkForCommands(message, username)
                            youtubeMessage = YouTubeMessageFromTwitch(username, message)
                            self.twitchMessagesToSave.append(youtubeMessage.toMongoObject(self.bot))

                for l in parts:
                    if "End of /NAMES list" in l:
                        self.MOTD = True

    def start(self, run_event):
        while run_event.is_set():
            self.readbuffer = self.readbuffer + self.s.recv(1024)
            temp = string.split(self.readbuffer, "\n")
            self.readbuffer = temp.pop()

            for line in temp:
                self.parseLine(line)

            if (len(self.twitchMessagesToSave) > 0):
                mongoChat.insert_many(self.twitchMessagesToSave)
                self.twitchMessagesToSave = []

            sleep(1.0 / (100.0/30.0))
