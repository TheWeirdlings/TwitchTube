import json
import unittest
from unittest.mock import MagicMock, patch

from twitchtube.util.TimersManager import TimersManager

import redis
import config
REDIS = redis.from_url(config.redisURL)

class TimersManagerTestCase(unittest.TestCase):
    def test_execute(self):
        test_id = 'test-id'
        channel = 'test-channel'
        bot = {
            '_id': str(test_id),
            'twitch': channel,
        }
        bot_encoded = json.dumps(bot).encode()
        bots = [bot_encoded]
        timerManager = TimersManager()
        timerManager.create_timers = MagicMock()
        timerManager.send_timers = MagicMock()

        timerManager.execute(bots);

        timerManager.create_timers.assert_called_with(bot)
        timerManager.send_timers.assert_called_with(bot)

    def test_send_timers(self):
        test_id = 'test-id'
        channel = 'test-channel'
        bot = {
            '_id': str(test_id),
            'twitch': channel,
        }
        timerManager = TimersManager()
        timerManager.get_current_minute = MagicMock()
        timerManager.get_current_minute.return_value = 5
        timerManager.bot_timers[test_id] = {
            5: ['testing', 'testing2']
        }

        timerManager.send_timers(bot)

        message_saved = REDIS.rpop("TwitchMessageToSync")
        message_saved = json.loads(message_saved.decode())
        message_saved2 = REDIS.rpop("TwitchMessageToSync")
        message_saved2 = json.loads(message_saved2.decode())

        youtube_message1 = REDIS.rpop("YoutubeMessageToSync")
        youtube_message1 = json.loads(youtube_message1.decode())
        youtube_message2 = REDIS.rpop("YoutubeMessageToSync")
        youtube_message2 = json.loads(youtube_message2.decode())

        self.assertEqual(message_saved2['message'], ': testing')
        self.assertEqual(message_saved['message'], ': testing2')

        self.assertEqual(youtube_message2['message'], 'testing')
        self.assertEqual(youtube_message1['message'], 'testing2')
