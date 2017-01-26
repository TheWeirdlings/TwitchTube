import unittest
from unittest.mock import MagicMock
from bson.objectid import ObjectId
import json
import datetime

from twitchtube.twitch.FollowerManager import FollowerManager
from TwitchPythonApi.twitch_api import TwitchApi

import redis
import config
r = redis.from_url(config.redisURL)

class FollowerManagerTestCase(unittest.TestCase):
    """Tests for ``."""

    def setUp(self):
        self.channel = 'channel'
        self.testId = ObjectId()
        self.twitchAlertText = 'Yo'
        self.bot = {
            '_id': self.testId,
            'twitch': self.channel,
            'twitchOptions': {
                    'displayTwitchAlerts': True,
                    'twitchAlertText': self.twitchAlertText,
                }
            }
        self.twitchFollowerResponse = """
            {
              "_total": 1234,
              "_links": {
                "self": "https://api.twitch.tv/kraken/channels/test_user1/follows?direction=DESC&limit=25",
                "next": "https://api.twitch.tv/kraken/channels/test_user1/follows?cursor=1364170340354965000&direction=DESC&limit=25"
              },
              "_cursor": "1364170340354965000",
              "follows": [
                {
                  "created_at": "[createdDate]",
                  "_links": {
                    "self": "https://api.twitch.tv/kraken/users/test_user2/follows/channels/test_user1"
                  },
                  "notifications": true,
                  "user": {
                    "_links": {
                      "self": "https://api.twitch.tv/kraken/users/test_user2"
                    },
                    "type": "user",
                    "bio": "test user's bio",
                    "logo": null,
                    "display_name": "test_user2",
                    "created_at": "2013-02-06T21:21:57Z",
                    "updated_at": "2013-02-13T20:59:42Z",
                    "_id": 40091581,
                    "name": "test_user2"
                  }
                }
              ]
            }
            """

    # def tearDown(self):
    #     mongoChat.delete_many({})

    def test_sendsMessageAboutNewFollower(self):
        twitchApi = TwitchApi()

        followerTime = datetime.datetime.now()
        followerTime = followerTime + datetime.timedelta(0,10)

        twitchFollowerResponse = self.twitchFollowerResponse.replace("[createdDate]", followerTime.isoformat())
        twitchApi.getFollowers = MagicMock(return_value=twitchFollowerResponse)

        followerManager = FollowerManager(self.bot, None, twitchApi)
        followerManager.exectute()

        messageSaved = r.lpop("twtichMessageToSync" + str(self.testId))
        messageSaved = json.loads(messageSaved.decode())

        self.assertEqual(messageSaved['message'], ": " + self.twitchAlertText)

    def test_doesNotSendMessageWhenFollowerIsBeforeNow(self):
        twitchApi = TwitchApi()

        followerTime = datetime.datetime.now()
        followerTime = followerTime + datetime.timedelta(0, -10)

        twitchFollowerResponse = self.twitchFollowerResponse.replace("[createdDate]", followerTime.isoformat())
        twitchApi.getFollowers = MagicMock(return_value=twitchFollowerResponse)

        followerManager = FollowerManager(self.bot, None, twitchApi)
        followerManager.exectute()

        messageSaved = r.lpop("twtichMessageToSync" + str(self.testId))

        self.assertFalse(messageSaved)

    def test_doesNotSendMessageWhenBotHasFollowMessageDisabled(self):
        twitchApi = TwitchApi()

        followerTime = datetime.datetime.now()
        followerTime = followerTime + datetime.timedelta(0, 10)

        twitchFollowerResponse = self.twitchFollowerResponse.replace("[createdDate]", followerTime.isoformat())
        twitchApi.getFollowers = MagicMock(return_value=twitchFollowerResponse)

        self.bot['twitchOptions']['displayTwitchAlerts'] = False

        followerManager = FollowerManager(self.bot, None, twitchApi)
        followerManager.exectute()

        messageSaved = r.lpop("twtichMessageToSync" + str(self.testId))
        
        self.assertFalse(messageSaved)
