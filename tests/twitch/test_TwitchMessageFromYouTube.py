import unittest

from twitchtube.models.YoutubeMessageCollection import YoutubeMessageCollection
from twitchtube.models.YoutubeMessageModel import YouTubeMessageModel

class YouTubeMessageModelTestCase(unittest.TestCase):
    """Tests for ``."""

    def test_getNextMessageToSend(self):
        testId = 1234
        bot = {'_id': testId}

        model = YouTubeMessageModel(bot)
        objectToSend = model.getNextMessageToSend();

        print("SDF")
        print(objectToSend)

        # self.assertEqual(mongoObject['sent'], False)
        # self.assertTrue(mongoObject['date'])
