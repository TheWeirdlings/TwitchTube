import unittest
from unittest.mock import MagicMock
import socket
import threading
from bson.objectid import ObjectId
from pymongo import MongoClient

from twitchtube.twitch.TwitchChatSender import TwitchChatSender
from twitchtube.models.TwitchMessageCollection import TwitchMessageCollection
from twitchtube.models.TwitchMessageModel import TwitchMessageModel

# @TODO: Move somwehre else?
import config
client = MongoClient(config.mongoUrl)
db = client[config.database]
mongoChat = db.twitchMessages

class TwitchChatSenderTestCase(unittest.TestCase):
    """Tests for ``."""

    def setUp(self):
        # set up fake bot
        twitchFromPrefix = "(From Twitch)"
        testId = ObjectId()
        self.channel = 'channel'
        self.bot = {
            '_id': testId,
            'twitch': self.channel,
            }

    def tearDown(self):
        mongoChat.delete_many({})

    # @TODO: Move to a generator helper class for tests?
    def createMessage(self):
        # set up collection
        twitchMessageCollection = TwitchMessageCollection(self.bot);

        # create message
        author = "test author"
        message = "test message"
        youtubeId = 1234
        message = TwitchMessageModel(author, message, youtubeId, self.bot['_id'])
        mongoObject = message.toMongoObject()

        # save the message to mongo
        # @TODO: save to test database
        twitchMessageCollection.saveChat(mongoObject)

        return message

    def test_sendTwitchMessge(self):
        messageModel = self.createMessage()

        # socketMock = socket.socket()
        socketMock = MagicMock()
        socketMock.send = MagicMock(return_value=True)

        run_event = threading.Event()
        run_event.is_set = MagicMock(return_value=True)

        twitchChatSender = TwitchChatSender(socketMock, run_event, self.bot)
        twitchChatSender.sendMessageFromQueue();

        sentChatMessage = mongoChat.find_one()

        self.assertTrue(sentChatMessage['sent'])
        socketMock.send.assert_called_with("PRIVMSG " + "#" + self.channel + " :" + messageModel.getMessage() + "\r\n")
