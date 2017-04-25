"""Tests for TwitchChatSender."""
import unittest
from unittest.mock import MagicMock
import threading
from bson.objectid import ObjectId
from pymongo import MongoClient

from twitchtube import TwitchChatSenderWorker
from twitchtube.models.TwitchMessageCollection import TwitchMessageCollection
from twitchtube.models.TwitchMessageModel import TwitchMessageModel

class RandomSub(object):
    def execute(self):
        pass

class TwitchChatSenderTestCase(unittest.TestCase):
    """Tests for TwitchChatSender."""

    def setUp(self):
        # set up fake bot
        test_id = ObjectId()
        self.channel = 'channel'
        self.bot = {
            '_id': test_id,
            'twitch': self.channel,
            }

    def test_notifiy_subscribers(self):
        '''Tests the notify subscribers'''
        sub = RandomSub()
        sub.execute = MagicMock()

        twitch_sender = TwitchChatSenderWorker()
        twitch_sender.register(sub)
        twitch_sender.notifiy_subscribers()

        self.assertTrue(sub.execute.called)

    def test_send_twitch_messge(self):
        '''Tests send twitch message'''
        socket_mock = MagicMock()
        socket_mock.send = MagicMock(return_value=True)

        channel = 'example-channel'
        message = 'example-message'
        twitch_sender = TwitchChatSenderWorker()
        twitch_sender.send_twitch_messge(channel, message)

        socket_mock.send.assert_called_with("PRIVMSG " + "#" + channel + " :" + message + "\r\n")

    def test_send_message_from_queue(self):
        pass

    def test_connect_to_channels(self):
        pass
    
    def test_get_channels(self):
        pass
    
    def test_parse_line(self):
        pass
    
    def test_read_socket(self):
        pass