import unittest
import json
from bson.objectid import ObjectId

from twitchtube.util.EmojiAssigner import EmojiAssigner

import redis
import config
r = redis.from_url(config.redisURL)

class EmojiAssignerTestCase(unittest.TestCase):
    """Tests for ``."""

    def test_ShouldAssignUsersTwoDifferentEmojis(self):
        username = 'test-1'
        username2 = 'test-2'

        emojiAssigner = EmojiAssigner(bot = {});

        emoji1 = emojiAssigner.getEmojiForUser(username)
        emoji2 = emojiAssigner.getEmojiForUser(username2)

        self.assertFalse(emoji1 == emoji2)

        emoji1 = emojiAssigner.getEmojiForUser(username)
        emoji2 = emojiAssigner.getEmojiForUser(username2)

        self.assertFalse(emoji1 == emoji2)
        self.assertTrue(emoji1 == emoji1)
        self.assertTrue(emoji2 == emoji2)
