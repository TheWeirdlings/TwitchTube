import unittest
from pymongo import MongoClient
from bson.objectid import ObjectId

from twitchtube.models.TwitchMessageCollection import TwitchMessageCollection
from twitchtube.models.TwitchMessageModel import TwitchMessageModel

# @TODO: Move somwehre else?
import config
client = MongoClient(config.mongoUrl)
db = client[config.database]
mongoYTChat = db.twitchMessages

class TwitchMessageCollectionTestCase(unittest.TestCase):
    """Tests for ``."""

    def setUp(self):
        # set up fake bot
        twitchFromPrefix = "(From Twitch)"
        self.testId = ObjectId()
        self.bot = {'_id': self.testId}

    def tearDown(self):
        mongoYTChat.delete_many({})

    def createTwitchMessage(self):
        # set up collection
        twitchMessageCollection = TwitchMessageCollection(self.bot);

        # create message
        author = "test author"
        message = "test message"
        youTubeMessageFromTwitch = TwitchMessageModel(author, message, self.testId, self.testId)
        mongoObject = youTubeMessageFromTwitch.toMongoObject()

        # save the message to mongo
        # @TODO: save to test database
        twitchMessageCollection.saveChat(mongoObject)


    def test_getNextMessageToSend(self):
        # create a message that is ready to send
        self.createTwitchMessage()

        # use the collection to get the message
        twitchMessageCollection = TwitchMessageCollection(self.bot);
        getNextMessageToSend = twitchMessageCollection.getNextMessageToSend()

        # test that it exists
        self.assertTrue(getNextMessageToSend)

    def test_markSent(self):
        # create a message that is ready to send
        self.createTwitchMessage()

        # use the collection to get the message
        twitchMessageCollection = TwitchMessageCollection(self.bot);
        getNextMessageToSend = twitchMessageCollection.getNextMessageToSend()

        # test that it exists
        self.assertTrue(getNextMessageToSend)

        # mark the message as sent
        twitchMessageCollection.markSent()

        # test try to get the message again
        getNextMessageToSendAgain = twitchMessageCollection.getNextMessageToSend()

        # test it does not exist
        self.assertFalse(getNextMessageToSendAgain)
