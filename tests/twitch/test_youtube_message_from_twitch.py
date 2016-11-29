import unittest

from twitchtube.twitch.YouTubeMessageFromTwitch import YouTubeMessageFromTwitch

class YouTubeMessageFromTwitchTestCase(unittest.TestCase):
    """Tests for ``."""

    def test_toMongoObject(self):
        twitchFromPrefix = "(From Twitch)"
        testId = 1234
        author = "test author"
        message = "test message"

        bot = {'_id': testId}

        youTubeMessageFromTwitch = YouTubeMessageFromTwitch(author, message)
        mongoObject = youTubeMessageFromTwitch.toMongoObject(bot)

        self.assertEquals(mongoObject['bot_id'], testId)
        self.assertEquals(mongoObject['message'], twitchFromPrefix + " " + author + ": " + message)
        self.assertEquals(mongoObject['sent'], False)
        self.assertTrue(mongoObject['date'])
