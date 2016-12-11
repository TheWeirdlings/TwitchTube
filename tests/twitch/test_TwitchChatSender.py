import unittest

from twitchtube.twitch.TwitchChatSender import TwitchChatSender

class TwitchChatSenderModelTestCase(unittest.TestCase):
    """Tests for ``."""

    def test_sendTwitchMessge(self):
        twitchChatSender = TwitchChatSender()
