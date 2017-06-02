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
    first_start = False
    twitch = bot['twitch']
    twitch_streams = twitch_api.streams.getStreams(twitch)
    twitch_streams = json.loads(twitch_streams)
    if 'stream' in twitch_streams and twitch_streams['stream']:
        active = True
    print((twitch_streams['stream']), flush=True)
    bot_id = bot['_id']
    if bot_id not in bot_status:
        bot_status[bot_id] = active
        first_start = True

    past_status = bot_status[bot_id]
    print(active, flush=True)
    if first_start or (active == True and past_status == False):
        bot_action = {
            "bot_id": str(bot_id),
            "status": 'restart',
        }
        REDIS.rpush(REDIS_COMMAND_QUEUE, json.dumps(bot_action))
        first_start = False

    if active == False and past_status == True:
        bot_action = {
            "bot_id": str(bot_id),
            "status": 'stop',
        }
        REDIS.rpush(REDIS_COMMAND_QUEUE, json.dumps(bot_action))

    bot_status[bot_id] = active

def check_youtube_stream(bot):
    active = False
    first_start = False
    channel_id = bot['youtube']
    streams = live_streams.get_live_streams_list(YOUTUBE, channel_id)
    print(streams, flush=True)
    if len(streams) > 0:
        active = True

    bot_id = bot['_id']
    if bot_id not in bot_status:
        bot_status[bot_id] = active
        first_start = True

    past_status = bot_status[bot_id]
    if first_start or (active == True and past_status == False):
        bot_action = {
            "bot_id": str(bot_id),
            "status": 'restart',
        }
        REDIS.rpush(REDIS_COMMAND_QUEUE, json.dumps(bot_action))
        first_start = False

    if active == False and past_status == True:
        bot_action = {
            "bot_id": str(bot_id),
            "status": 'stop',
        }
        REDIS.rpush(REDIS_COMMAND_QUEUE, json.dumps(bot_action))

    bot_status[bot_id] = active

def listen():
    while 1:
        # Get bots that are listening
        DB.twitchtubeBots.find({
            '_id': ObjectId(bot_id),
            'options.watchStream': True,
            })
        # bot = {
        #     '_id': 'testing',
        #     # 'twitch': 'themisterholliday',
        #     'youtube': 'EiEKGFVDOWZZcVduaVhtVjNTNVVoRVdyb2pJdxIFL2xpdmU'
        # }

        if 'twitch' in bot:
            check_twitch_stream(bot)

        # if 'youtube' in bot and 'twitch' not in bot:
        #     check_youtube_stream(bot)

        sleep(15)

if __name__ == '__main__':
    ARGS = argparser.parse_args()
    YOUTUBE = get_authenticated_service(ARGS)
    listen()
