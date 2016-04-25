import sys
from pymongo import MongoClient
from bson.objectid import ObjectId

availableActions = ['create', 'read', 'update', 'delete']
availableItems = ['bot', 'user', 'chat', 'command', 'timer']

client = MongoClient('mongodb://localhost:27017/')
db = client.twitchtube

from init import get_authenticated_service
from youtubelivestreaming.live_broadcasts import get_live_broadcasts

from oauth2client.tools import argparser, run_flow

import datetime

class TwitchtubeBot(object):
    def __init__(self, name, twitch, youtube):
        self.name = name
        self.twitch = twitch
        self.youtube = youtube

    def toMongoObject(self):
        mongoMessage = {
            "twitch": self.twitch,
            "youtube": self.youtube,
            "name": self.name,
            "date_created": datetime.datetime.utcnow()
        }
        return mongoMessage

class Command(object):
    def __init__(self, botId, command, message):
        self.botId = botId
        self.command = command
        self.message = message

    def toMongoObject(self):
        mongoMessage = {
            "botId": ObjectId(self.botId),
            "command": self.command,
            "message": self.message,
            "date_created": datetime.datetime.utcnow()
        }
        return mongoMessage

if __name__ == "__main__":

    argparser.add_argument('--action', help='Action')
    argparser.add_argument('--item', help='Item')
    args = argparser.parse_args()

    #Take action CRUD - or other
    action = args.action#sys.argv[1]
    if action not in availableActions:
         raise Exception('Action is not available. Try:')#implode?

    #Take object (Bot, User, Chat, Command, Timer)
    item = args.item#sys.argv[2]
    if item not in availableItems:
         raise Exception('Item is not available. Try:')#implode?

    print "\n"

    if action == "read":
        if item == "bot":
            bots = db.twitchtubeBots.find()
            for bot in bots:
                for key, value in bot.iteritems() :
                    print key, value
                print "\n"
        elif item == "command":
            commands = db.commands.find()
            for command in commands:
                for key, value in command.iteritems() :
                    print key, value
                print "\n"

    elif action == "create":
        if item == "bot":
            youtube = get_authenticated_service(args)
            youTubeLiveChatId = get_live_broadcasts(youtube)
            botAlias = raw_input('Enter the name of your bot: ')
            twitch = raw_input('Enter the Twitch Channel: ')

            tb = TwitchtubeBot(botAlias, twitch, youTubeLiveChatId);
            db.twitchtubeBots.insert(tb.toMongoObject())

        elif item == "command":
            botId = raw_input('Enter the bot id for the command: ')
            command = raw_input('Enter the command (ex: !testingstuffs): ')
            message = raw_input('What message will be displayed after the command?: ')

            commandDoc = Command(botId, command, message);
            db.commands.insert(commandDoc.toMongoObject())
