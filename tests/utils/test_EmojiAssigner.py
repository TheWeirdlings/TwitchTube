import unittest

from twitchtube.util.EmojiAssigner import EmojiAssigner

class EmojiAssignerTestCase(unittest.TestCase):
    """Tests for ``."""

    def test_ShouldAssignUsersTwoDifferentEmojis(self):
        username = 'test-1'
        username2 = 'test-2'

        emoji_assigner = EmojiAssigner(bot={})

        emoji1 = emoji_assigner.getEmojiForUser(username)
        emoji2 = emoji_assigner.getEmojiForUser(username2)

        self.assertFalse(emoji1 == emoji2)

        emoji1 = emoji_assigner.getEmojiForUser(username)
        emoji2 = emoji_assigner.getEmojiForUser(username2)

        self.assertFalse(emoji1 == emoji2)
        self.assertTrue(emoji1 == emoji1)
        self.assertTrue(emoji2 == emoji2)
