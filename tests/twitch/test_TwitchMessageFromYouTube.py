import unittest
from pymongo import MongoClient

from twitchtube.models.YoutubeMessageCollection import YoutubeMessageCollection
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

# @TODO: Move somwehre else?
import config
client = MongoClient(config.mongoUrl)
db = client[config.database]
mongoYTChat = db.youtubeMessages

class YouTubeMessageModelTestCase(unittest.TestCase):
    """Tests for ``."""

    def setUp(self):
        # set up fake bot
        twitchFromPrefix = "(From Twitch)"
        testId = 1234
        self.bot = {'_id': testId}

    def tearDown(self):
        mongoYTChat.remove({})

    def createYoutubeMessage(self):
        # set up collection
        youtubeMessageCollection = YoutubeMessageCollection(self.bot);

        # create message
        author = "test author"
        message = "test message"
        youTubeMessageFromTwitch = YoutubeMessageModel(author, message)
        mongoObject = youTubeMessageFromTwitch.toMongoObject(self.bot)

        # save the message to mongo
        # @TODO: save to test database
        youtubeMessageCollection.saveChat(mongoObject)


    def test_getNextMessageToSend(self):
        # create a message that is ready to send
        self.createYoutubeMessage()

        # use the collection to get the message
        youtubeMessageCollection = YoutubeMessageCollection(self.bot);
        getNextMessageToSend = youtubeMessageCollection.getNextMessageToSend()

        # test that it exists
        self.assertTrue(getNextMessageToSend)
