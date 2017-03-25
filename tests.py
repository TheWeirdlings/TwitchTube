import unittest

from tests.test_example import PrimesTestCase

from tests.models.test_TwitchMessageModel import TwitchMessageModelTestCase
from tests.models.test_TwitchMessageCollection import TwitchMessageCollectionTestCase
from tests.models.test_YoutubeMessageModel import YoutubeMessageModelTestCase
from tests.models.test_YoutubeMessageCollection import YoutubeMessageCollectionTestCase

from tests.twitch.test_TwitchChatSender import TwitchChatSenderTestCase
from tests.twitch.test_FollowerManager import FollowerManagerTestCase

from tests.utils.test_EmojiAssigner import EmojiAssignerTestCase

if __name__ == '__main__':
    unittest.main()
