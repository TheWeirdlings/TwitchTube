from pymongo import MongoClient
from time import sleep
from dateutil import parser
from datetime import datetime, timezone

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
        # @TODO: Store this and load from redis
        self.lastSyncedMessageDate = datetime.now(timezone.utc)
        # self.commands = self.mongoCommands.find({"botId": str(bot['_id'])})

        self.nextPageToken = None;

    def applyCommands(self, message):
        self.commands = self.mongoCommands.find({"botId": str(self.botId)})
        for command in self.commands:
            if (command['command'] == message['snippet']['displayMessage'] and twitchFromPrefix not in message['snippet']['displayMessage']):
                #WE can send on the same thread as we are polling chat, so let's just queue this message up
                youtubeMessage = YoutubeMessageModel("", command['message'], False)
                self.mongoTwitchChat.insert(youtubeMessage.toMongoObject(self.bot))

    def save(self, messages):
        mongoMessagesToSaveToMongo = []

        for message in messages:
            #Don't save chat sent from the bot - these are commands and timers
            if (message['authorDetails']['displayName'] == 'Twitchtube'):
                continue

            messageToSave = TwitchMessageModel(message['authorDetails']['displayName'], message['snippet']['displayMessage'], message['id'], self.botId)

            # Confirm that we have a new message
            messagePublishedDate = message['snippet']['publishedAt']
            messagePublishedDate = parser.parse(messagePublishedDate)

            if self.lastSyncedMessageDate < messagePublishedDate:
                print("Saving", flush=True)
                messageToSave.save()
                self.lastSyncedMessageDate = messagePublishedDate

    def saveChat(self):
        response = live_messages.list_messages(self.youtubeAuth, self.livechat_id, self.nextPageToken)

        self.nextPageToken = response['nextPageToken']
        pollingIntervalInMillis = response['pollingIntervalMillis']
        pollingIntervaLInSeconds = pollingIntervalInMillis/1000
        messages = response.get("items", [])

        self.save(messages)

        #TODO: I think this isn't fast enough :(
        sleep(pollingIntervaLInSeconds)

    def run(self, run_event):
        while run_event.is_set():
            self.saveChat()
