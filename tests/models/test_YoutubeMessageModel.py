"""Tests for YoutubeMessageModel."""
import unittest
import json

from twitchtube.models.YoutubeMessageModel import YoutubeMessageModel

import redis
import config
REDIS = redis.from_url(config.redisURL)

class YoutubeMessageModelTestCase(unittest.TestCase):
    """Tests for YoutubeMessageModel."""
    def test_save(self):
        '''Test that message is saved to redis'''
        prefix = "(From Twitch)"
        test_id = 1234
        author = "test author"
        message = "test message"

        bot = {'_id': test_id}

        model = YoutubeMessageModel(author, message, bot)
        model.save()

        message_saved = REDIS.rpop("YoutubeMessageToSync")
        message_saved = json.loads(message_saved.decode())

        self.assertEqual(message_saved['bot_id'], str(test_id))
        self.assertEqual(message_saved['message'], prefix + " " + author + ": " + message)
        self.assertEqual(message_saved['sent'], False)
        self.assertTrue(message_saved['date'])

    def test_save_without_prefix(self):
        '''Test that a message is saved without the
        prefix'''
        test_id = 1234
        author = "test author"
        message = "test message"

        bot = {
            '_id': test_id,
            'options': {
                'displayFromMessages': False
                }
            }

        model = YoutubeMessageModel(author, message, bot)
        model.save()

        message_saved = REDIS.rpop("YoutubeMessageToSync")
        message_saved = json.loads(message_saved.decode())

        self.assertEqual(message_saved['bot_id'], str(test_id))
        self.assertEqual(message_saved['message'], author + ": " + message)
        self.assertEqual(message_saved['sent'], False)
        self.assertTrue(message_saved['date'])
