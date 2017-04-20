import unittest
from pymongo import MongoClient
from bson.objectid import ObjectId

from twitchtube.models.TwitchMessageCollection import TwitchMessageCollection
from twitchtube.models.TwitchMessageModel import TwitchMessageModel

class TwitchMessageCollectionTestCase(unittest.TestCase):
    """Tests for ``."""

    def setUp(self):
        # set up fake bot
        self.test_id = ObjectId()
        self.bot = {'_id': self.test_id}

    def test_get_next_message_to_send(self):
        '''Test getting the next message off the queue'''
        author = 'author'
        text = 'text'
        youtube_id = 'youtube_id'

        # create a message that is ready to send
        twitch_message = TwitchMessageModel(author, text, youtube_id, self.bot)
        twitch_message.save()

        # use the collection to get the message
        twitch_message_collection = TwitchMessageCollection()
        next_message = twitch_message_collection.get_next_message_to_send()

        # test that it exists
        self.assertTrue(next_message)