import unittest
from bson.objectid import ObjectId

from twitchtube.models.TwitchMessageModel import TwitchMessageModel

class TwitchMessageModelTestCase(unittest.TestCase):
    """Tests for ``."""

    def test_toMongoObject(self):
        twitchFromPrefix = "(From YouTube)"
        testId = ObjectId()
        author = "test author"
        message = "test message"

        bot = {'_id': testId}

        twitchMessageFromTwitch = TwitchMessageModel(author, message, testId, testId)
        mongoObject = twitchMessageFromTwitch.toMongoObject()

        self.assertEqual(mongoObject['bot_id'], testId)
        self.assertEqual(mongoObject['message'], twitchFromPrefix + " " + author + ": " + message)
        self.assertEqual(mongoObject['sent'], False)
        self.assertTrue(mongoObject['date'])
