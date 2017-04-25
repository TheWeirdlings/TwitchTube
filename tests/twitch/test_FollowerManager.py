"""Tests for FollowerManager."""
import unittest
from unittest.mock import MagicMock
from bson.objectid import ObjectId
import json
import datetime
import pytz

from twitchtube.twitch.FollowerManager import FollowerManager
from TwitchPythonApi.twitch_api import TwitchApi

import redis
import config
REDIS = redis.from_url(config.redisURL)

import config
from pymongo import MongoClient
MONGO = MongoClient(config.mongoUrl)
DATABASE = MONGO[config.database]

class FollowerManagerTestCase(unittest.TestCase):
    """Tests for FollowerManager."""
    def setUp(self):
        self.channel = 'channel'
        self.test_id = ObjectId()
        self.twitch_alert_text = 'Yo'
        self.bot = {
            '_id': str(self.test_id),
            'twitch': self.channel,
            'twitchOptions': {
                'displayTwitchAlerts': True,
                'twitchAlertText': self.twitch_alert_text,
                }
            }
        self.bot_encoded = json.dumps(self.bot).encode()
        self.twitch_follower_response = """
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

    def test_sends_message_about_new_follower(self):
        '''Tests that a message is sent when a new user
        follows'''
        twitch_api = TwitchApi()

        follower_time = datetime.datetime.now(pytz.UTC)
        follower_time = follower_time + datetime.timedelta(0, 10)

        twitch_follower_response = self.twitch_follower_response.replace("[createdDate]", \
          follower_time.isoformat())
        twitch_api.getFollowers = MagicMock(return_value=twitch_follower_response)

        self.bot['twitchOptions']['thankNewFollowers'] = True
        self.bot_encoded = json.dumps(self.bot).encode()

        follower_manager = FollowerManager(DATABASE, twitch_api)
        follower_manager.execute([self.bot_encoded])

        message_saved = REDIS.rpop("TwitchMessageToSync")
        # Two pops because we have the thank you message
        message_saved = REDIS.rpop("TwitchMessageToSync")
        message_saved = json.loads(message_saved.decode())

        self.assertEqual(message_saved['message'], ": " + self.twitch_alert_text)

    def test_doesNotSendMessageWhenFollowerIsBeforeNow(self):
        REDIS.ltrim("TwitchMessageToSync", 0, 0)
        twitch_api = TwitchApi()

        follower_time = datetime.datetime.now(pytz.UTC)
        follower_time = follower_time + datetime.timedelta(0, -10)

        twitch_follower_response = self.twitch_follower_response.replace("[createdDate]", \
          follower_time.isoformat())
        twitch_api.getFollowers = MagicMock(return_value=twitch_follower_response)

        follower_manager = FollowerManager(DATABASE, twitch_api)
        follower_manager.execute([self.bot_encoded])

        message_saved = REDIS.rpop("TwitchMessageToSync")

        self.assertFalse(message_saved)

    def test_doesNotSendMessageWhenBotHasFollowMessageDisabled(self):
        REDIS.ltrim("TwitchMessageToSync", 0, 0)
        twitch_api = TwitchApi()

        follower_time = datetime.datetime.now(pytz.UTC)
        follower_time = follower_time + datetime.timedelta(0, 10)

        twitch_follower_response = self.twitch_follower_response.replace("[createdDate]", \
          follower_time.isoformat())
        twitch_api.getFollowers = MagicMock(return_value=twitch_follower_response)

        self.bot['twitchOptions']['displayTwitchAlerts'] = False
        self.bot_encoded = json.dumps(self.bot).encode()

        follower_manager = FollowerManager(DATABASE, twitch_api)
        follower_manager.execute([self.bot_encoded])

        message_saved = REDIS.rpop("TwitchMessageToSync")

        self.assertFalse(message_saved)

    def test_sendsThankYouMessageToFollower(self):
        twitch_api = TwitchApi()

        follower_time = datetime.datetime.now(pytz.UTC)
        follower_time = follower_time + datetime.timedelta(0, 10)

        twitch_follower_response = self.twitch_follower_response.replace("[createdDate]", \
          follower_time.isoformat())
        twitch_api.getFollowers = MagicMock(return_value=twitch_follower_response)

        self.bot['twitchOptions']['thankNewFollowers'] = True
        self.bot_encoded = json.dumps(self.bot).encode()

        follower_manager = FollowerManager(DATABASE, twitch_api)
        follower_manager.execute([self.bot_encoded])

        message_saved = REDIS.rpop("TwitchMessageToSync")
        REDIS.rpop("TwitchMessageToSync")
        message_saved = json.loads(message_saved.decode())

        self.assertEqual(message_saved['message'], ": Thanks for following, @test_user2!")
