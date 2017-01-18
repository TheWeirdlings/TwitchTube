import unittest
import json

from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

import redis
import config
r = redis.from_url(config.redisURL)

class YoutubeMessageModelTestCase(unittest.TestCase):
    """Tests for ``."""

    def test_shouldCreateMongoObject(self):
        twitchFromPrefix = "(From Twitch)"
        testId = 1234
        author = "test author"
        message = "test message"

        bot = {'_id': testId}

        youTubeMessageFromTwitch = YoutubeMessageModel(author, message, bot)
        mongoObject = youTubeMessageFromTwitch.toMongoObject(bot)

        self.assertEqual(mongoObject['bot_id'], testId)
        self.assertEqual(mongoObject['message'], twitchFromPrefix + " " + author + ": " + message)
        self.assertEqual(mongoObject['sent'], False)
        self.assertTrue(mongoObject['date'])

    def test_shouldSaveToRedis(self):
        twitchFromPrefix = "(From Twitch)"
        testId = 1234
        author = "test author"
        message = "test message"

        bot = {'_id': testId}

        youTubeMessageFromTwitch = YoutubeMessageModel(author, message, bot)
        youTubeMessageFromTwitch.save()

        messageSaved = r.lpop("youtubeMessageToSync" + str(testId))
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

        youTubeMessageFromTwitch = YoutubeMessageModel(author, message, bot)
        youTubeMessageFromTwitch.save()

        messageSaved = r.lpop("youtubeMessageToSync" + str(testId))
        messageSaved = json.loads(messageSaved.decode())

        self.assertEqual(messageSaved['bot_id'], str(testId))
        self.assertEqual(messageSaved['message'], author + ": " + message)
        self.assertEqual(messageSaved['sent'], False)
        self.assertTrue(messageSaved['date'])
