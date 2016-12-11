import unittest

from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

class YouTubeMessageFromTwitchTestCase(unittest.TestCase):
    """Tests for ``."""

    def test_toMongoObject(self):
        twitchFromPrefix = "(From Twitch)"
        testId = 1234
        author = "test author"
        message = "test message"

        bot = {'_id': testId}

        youTubeMessageFromTwitch = YoutubeMessageModel(author, message)
        mongoObject = youTubeMessageFromTwitch.toMongoObject(bot)

        self.assertEqual(mongoObject['bot_id'], testId)
        self.assertEqual(mongoObject['message'], twitchFromPrefix + " " + author + ": " + message)
        self.assertEqual(mongoObject['sent'], False)
        self.assertTrue(mongoObject['date'])
