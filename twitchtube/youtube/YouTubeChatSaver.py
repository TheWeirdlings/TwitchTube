from pymongo import MongoClient
from time import sleep

import config
from youtubelivestreaming import live_messages
from twitchtube.models.TwitchMessageModel import TwitchMessageModel
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

import json

twitchFromPrefix = "(From Twitch)"

class YoutubeChatSaver(object):
    def __init__(self, bot, youtubeAuth):
        self.youtubeAuth = youtubeAuth

        client = MongoClient(config.mongoUrl)
        db = client[config.database]
        self.mongoCommands = db.commands
        self.mongoYTChat = db.youtubeMessages
        self.mongoTwitchChat = db.twitchMessages
        self.bot = bot
        self.botId = bot['_id']

        self.livechat_id = bot['youtube']
        # self.commands = self.mongoCommands.find({"botId": str(bot['_id'])})

    def applyCommands(self, message):
        self.commands = self.mongoCommands.find({"botId": str(self.botId)})
        for command in self.commands:
            if (command['command'] == message['snippet']['displayMessage'] and twitchFromPrefix not in message['snippet']['displayMessage']):
                #WE can send on the same thread as we are polling chat, so let's just queue this message up
                youtubeMessage = YoutubeMessageModel("", command['message'], False)
                self.mongoTwitchChat.insert(youtubeMessage.toMongoObject(self.bot))

    def save(self, messages):
        mongoMessagesToSaveToMongo = []
        #TODO: Get bulk to work
        #bulkop = self.mongoYTChat.initialize_ordered_bulk_op()

        for message in messages:
            #Don't save chat sent from the bot - these are commands and timers
            if (message['authorDetails']['displayName'] == 'Twitchtube'):
                continue

            messageToSave = TwitchMessageModel(message['authorDetails']['displayName'], message['snippet']['displayMessage'], message['id'], self.botId)
            mongoMessagesToSaveToMongo.append(messageToSave.toMongoObject())

            #Confirm that we have a new message
            if self.mongoYTChat.find_one({'youtubeId': message['id']}) is None:
                self.mongoYTChat.insert(messageToSave.toMongoObject())
                self.applyCommands(message);
            #bulkop.find({'youtubeId': message['id']}).upsert().update(messageToSave.toMongoObject())

        #TODO: How do we check if there are bluk operations
        # if len(mongoMessagesToSaveToMongo) > 0:
        #     bulkop.execute()

    def run(self, run_event):
        nextPageToken = None;
        prevMessage = None;
        while run_event.is_set():
            response = live_messages.list_messages(self.youtubeAuth, self.livechat_id, nextPageToken)

            nextPageToken = response['nextPageToken']
            pollingIntervalInMillis = response['pollingIntervalMillis']
            pollingIntervaLInSeconds = pollingIntervalInMillis/1000
            messages = response.get("items", [])

            self.save(messages)
            #TODO: I think this isn't fast enough :(
            sleep(pollingIntervaLInSeconds)
