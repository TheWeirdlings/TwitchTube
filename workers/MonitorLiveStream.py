from time import sleep
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

import config
import redis
REDIS = redis.from_url(config.redisURL)
REDIS_COMMAND_QUEUE = config.reddisBotCommandQueue
CLINET = MongoClient(config.mongoUrl)
DB = CLINET[config.database]

YOUTUBE = None

from TwitchPythonApi.twitch_api import TwitchApi
from youtubelivestreaming import live_streams
from helpers import get_authenticated_service
from oauth2client.tools import argparser

bot_status = {}
twitch_api = TwitchApi()

def check_twitch_stream(bot):
    active = False
    twitch_streams = twitch_api.streams.getStreams('thehollidayinn')
    twitch_streams = json.loads(twitch_streams)
    if twitch_streams['stream']:
        active = True

    bot_id = bot['_id']
    if bot_id not in bot_status:
        bot_status[bot_id] = active
        return

    past_status = bot_status[bot_id]
    if past_status == False:
        bot_action = {
            "bot_id": str(bot_id),
            "status": 'restart',
        }
        REDIS.rpush(REDIS_COMMAND_QUEUE, json.dumps(bot_action))

    if past_status == True:
        bot_action = {
            "bot_id": str(bot_id),
            "status": 'stop',
        }
        REDIS.rpush(REDIS_COMMAND_QUEUE, json.dumps(bot_action))
        pass

    bot_status[bot_id] = active

def check_youtube_stream(bot):
    active = False
    twitch_streams = twitch_api.streams.getStreams('thehollidayinn')
    twitch_streams = json.loads(twitch_streams)
    channel_id = bot['youtube']
    streams = live_streams.get_live_streams_list(YOUTUBE, channel_id)

    if len(streams) > 0:
        active = True

    bot_id = bot['_id']
    if bot_id not in bot_status:
        bot_status[bot_id] = active
        return

    past_status = bot_status[bot_id]
    if past_status == False:
        bot_action = {
            "bot_id": str(bot_id),
            "status": 'restart',
        }
        REDIS.rpush(REDIS_COMMAND_QUEUE, json.dumps(bot_action))

    if past_status == True:
        bot_action = {
            "bot_id": str(bot_id),
            "status": 'stop',
        }
        REDIS.rpush(REDIS_COMMAND_QUEUE, json.dumps(bot_action))
        pass

    bot_status[bot_id] = active

def listen():
    while 1:
        # Get bots that are listening
        # DB.twitchtubeBots.find({
        #     '_id': ObjectId(bot_id),
        #     'watch_stream': True,
        #     })
        bot = {
            '_id': 'testing',
            'twitch': 'thehollidayinn'
        }

        if 'twitch' in bot:
            check_twitch_stream(bot)

        if 'youtube' in bot:
            check_youtube_stream(bot)

        sleep(30)

if __name__ == '__main__':
    ARGS = argparser.parse_args()
    YOUTUBE = get_authenticated_service(ARGS)
    listen()
