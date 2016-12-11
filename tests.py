import unittest

from tests.test_example import PrimesTestCase

from tests.models.test_YoutubeMessageModel import YoutubeMessageModelTestCase
from tests.models.test_YoutubeMessageCollection import YoutubeMessageCollectionTestCase

from tests.twitch.test_TwitchChatSender import TwitchChatSenderTestCase

if __name__ == '__main__':
    unittest.main()
