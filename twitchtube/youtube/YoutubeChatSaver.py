from pymongo import MongoClient
from time import sleep
from dateutil import parser
from datetime import datetime, timezone

import config
from youtubelivestreaming import live_messages
from twitchtube.models.TwitchMessageModel import TwitchMessageModel
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel
from twitchtube.util.CommandManager import CommandManager

import json

class YoutubeChatSaver(object):
    def __init__(self, bot, youtubeAuth, db):
        self.youtubeAuth = youtubeAuth
        self.bot = bot
        self.botId = bot['_id']
        self.livechat_id = bot['youtube']
        # @TODO: Store this and load from redis
        self.lastSyncedMessageDate = datetime.now(timezone.utc)
        self.nextPageToken = None;
        self.commandManager = CommandManager(db, bot)

    def save(self, messages):
        for message in messages:
            # Don't save chat sent from the bot - these are commands and timers
            # @TODO Abstract Author to constant
            if (message['authorDetails']['displayName'] == 'Twitchtube'):
                continue

            username = message['authorDetails']['displayName']
            messagecontent = message['snippet']['displayMessage']
            messageToSave = TwitchMessageModel(username, messagecontent, message['id'], self.bot)

            # Confirm that we have a new message
            messagePublishedDate = message['snippet']['publishedAt']
            messagePublishedDate = parser.parse(messagePublishedDate)

            if self.lastSyncedMessageDate < messagePublishedDate:
                messageToSave.save()
                self.lastSyncedMessageDate = messagePublishedDate

                #check commands
                commandMessage = self.commandManager.checkForCommands(messagecontent, username)
                if commandMessage is not None:
                    # @TODO Abstract Author to constant
                    commandMessageToSave = YoutubeMessageModel('', commandMessage, self.bot)
                    commandMessageToSave.save()

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
