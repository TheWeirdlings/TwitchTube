"""Tests for YoutubeMessageCollection."""
import unittest
from bson.objectid import ObjectId

from twitchtube.models.YoutubeMessageCollection import YoutubeMessageCollection
from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

class YoutubeMessageCollectionTestCase(unittest.TestCase):
    """Tests for YoutubeMessageCollection."""
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
        twitch_message = YoutubeMessageModel(author, text, self.bot)
        twitch_message.save()

        # use the collection to get the message
        youtube_message_collection = YoutubeMessageCollection()
        next_message = youtube_message_collection.get_next_message_to_send()

        # test that it exists
        self.assertTrue(next_message)
