import unittest
import json
from bson.objectid import ObjectId

from twitchtube.models.TwitchMessageModel import TwitchMessageModel

import redis
import config
r = redis.from_url(config.redisURL)

class TwitchMessageModelTestCase(unittest.TestCase):
    """Tests for ``."""

    def test_toMongoObject(self):
        twitchFromPrefix = "(From YouTube)"
        testId = ObjectId()
        author = "test author"
        message = "test message"

        bot = {'_id': testId}

        twitchMessageFromTwitch = TwitchMessageModel(author, message, testId, bot)
        mongoObject = twitchMessageFromTwitch.toMongoObject()

        self.assertEqual(mongoObject['bot_id'], testId)
        self.assertEqual(mongoObject['message'], twitchFromPrefix + " " + author + ": " + message)
        self.assertEqual(mongoObject['sent'], False)
        self.assertTrue(mongoObject['date'])

    def test_shouldSaveToRedis(self):
        twitchFromPrefix = "(From YouTube)"
        testId = 1234
        author = "test author"
        message = "test message"

        bot = {'_id': testId}

        model = TwitchMessageModel(author, message, "youtube-id", bot)
        model.save()

        messageSaved = r.lpop("twtichMessageToSync" + str(testId))
        messageSaved = json.loads(messageSaved.decode())

        self.assertEqual(messageSaved['bot_id'], str(testId))
        self.assertEqual(messageSaved['message'], twitchFromPrefix + " " + author + ": " + message)
        self.assertEqual(messageSaved['sent'], False)
        self.assertTrue(messageSaved['date'])

    def test_shouldSaveWithoutPrefixWhenBotHasOptionDisabled(self):
        testId = 1234
        author = "test author"
        message = "test message"

        bot = {
            '_id': testId,
            'options': {
                    'displayFromMessages': False
                }
            }

        model = TwitchMessageModel(author, message, "youtube-id", bot)
        model.save()

        messageSaved = r.lpop("twtichMessageToSync" + str(testId))
        messageSaved = json.loads(messageSaved.decode())

        self.assertEqual(messageSaved['bot_id'], str(testId))
        self.assertEqual(messageSaved['message'], author + ": " + message)
        self.assertEqual(messageSaved['sent'], False)
        self.assertTrue(messageSaved['date'])
