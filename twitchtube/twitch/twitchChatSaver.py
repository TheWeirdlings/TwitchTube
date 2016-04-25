import twitchConfig
from HTMLParser import HTMLParser
import cgi
import string
from time import sleep
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client.twitchtube
bots = db.twitchtubeBots
mongoChat = db.twitchMessages
mongoCommands = db.commands

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class YouTubeMessageFromTwitch(object):
    def __init__(self, author, text, addFromTwitch = True):
        message = ""
        if (addFromTwitch):
            message = "(From Twitch) "

        if (author):
            message = message + author + ": "

        self.message = message + text


    def toMongoObject(self, bot):
        # @TODO: Should we really pass the bot around this way?
        mongoMessage = {
            "bot_id": bot['_id'],
            "message": self.message,
            "sent": False,
            "date": datetime.datetime.utcnow()
        }
        return mongoMessage

class TwitchChatSaver(object):

    def __init__(self, incSocket, bot):
        self.readbuffer = ""
        self.MOTD = False
        self.CHANNEL = "#" + bot['twitch']

        self.twitchMessagesToSave = []
        self.s = incSocket

        self.commands = mongoCommands.find({"botId": str(ObjectId(bot['_id'])) })

        self.bot = bot

    def sendTwitchMessge(self, message):
        try:
            self.s.send("PRIVMSG " + self.CHANNEL + " :" + message + "\r\n")
        except UnicodeDecodeError:
            print 'Add support'

    def checkForCommands(self, line, username):
        self.commands = mongoCommands.find({"botId": str(ObjectId(self.bot['_id'])) })

        for command in self.commands:
            if (command['command'] in line):
                self.sendTwitchMessge(command['message'])

        if "!restart" in line:
            bots.update({'_id': self.bot['_id']}, {'$set': {'status': 'restart'}})
            self.sendTwitchMessge('Restarting...')

        # if "!stop" in line:
        #     bots.update({'_id': self.bot['_id']}, {'$set': {'status': 'stop'}})
        #     self.sendTwitchMessge('stoping..')

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
                        self.checkForCommands(line, username)

                        message = strip_tags(message)
                        message = cgi.escape(message)
                        if message:
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
