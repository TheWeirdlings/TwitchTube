'''Tests for Twitch Message Model'''
import unittest
import json

from twitchtube.models.TwitchMessageModel import TwitchMessageModel

import redis
import config
REDIS = redis.from_url(config.redisURL)

class TwitchMessageModelTestCase(unittest.TestCase):
    '''Tests for Twitch Message Model'''
    def test_save(self):
        '''Test that twitch message is saved to redis'''
        twitch_from_prefix = "(From YouTube)"
        test_id = 1234
        author = "test author"
        message = "test message"

        bot = {'_id': test_id}

        model = TwitchMessageModel(author, message, "youtube-id", bot)
        model.save()

        message_saved = REDIS.rpop("TwitchMessageToSync")
        message_saved = json.loads(message_saved.decode())

        generated_message = twitch_from_prefix + " " + author + ": " + message

        self.assertEqual(message_saved['bot_id'], str(test_id))
        self.assertEqual(message_saved['message'], generated_message)
        self.assertEqual(message_saved['sent'], False)
        self.assertTrue(message_saved['date'])

    def test_save_without_prefix(self):
        '''Test that a twitch message is saved without the
        youtube prefix'''
        test_id = 1234
        author = "test author"
        message = "test message"

        bot = {
            '_id': test_id,
            'options': {
                'displayFromMessages': False
                }
            }

        model = TwitchMessageModel(author, message, "youtube-id", bot)
        model.save()

        message_saved = REDIS.rpop("TwitchMessageToSync")
        message_saved = json.loads(message_saved.decode())

        self.assertEqual(message_saved['bot_id'], str(test_id))
        self.assertEqual(message_saved['message'], author + ": " + message)
        self.assertEqual(message_saved['sent'], False)
        self.assertTrue(message_saved['date'])
