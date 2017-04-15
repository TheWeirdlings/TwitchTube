'''Listen to REDIS for bot commands'''
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

def proccess_command(bot_id, action):
    '''Process command from Redis'''
    if action == 'start':
        mongo_bot = DB.twitchtubeBots.find_one({'_id': ObjectId(bot_id)})

        if mongo_bot is None:
            #@TODO: Log
            return

        cached_bot = REDIS.hget('TwitchtubeBotsById', bot_id)

        mongo_bot['active'] = True
        mongo_bot['_id'] = str(mongo_bot['_id'])

        if cached_bot is None:
            list_index = REDIS.lpush('TwitchtubeBots', json.dumps(mongo_bot))
            mongo_bot['list_index'] = list_index
            REDIS.hmset('TwitchtubeBotsById', {mongo_bot['_id']: json.dumps(mongo_bot)})
            return

        cached_bot = json.loads(cached_bot.decode())
        list_index = cached_bot['list_index']
        mongo_bot['active'] = True
        mongo_bot['_id'] = str(mongo_bot['_id'])
        mongo_bot['list_index'] = list_index
        REDIS.hmset('TwitchtubeBotsById', {mongo_bot['_id']: json.dumps(mongo_bot)})
        REDIS.lset('TwitchtubeBots', list_index - 1, json.dumps(mongo_bot))

    # @TODO: We need to set a variable on the bot for restart to let the scripts know
    if action == 'restart':
        mongo_bot = DB.twitchtubeBots.find_one({'_id': ObjectId(bot_id)})

        if mongo_bot is None:
            #@TODO: Log
            return

        cached_bot = REDIS.hget('TwitchtubeBotsById', bot_id)

        mongo_bot['active'] = True
        mongo_bot['_id'] = str(mongo_bot['_id'])

        if cached_bot is None:
            list_index = REDIS.lpush('TwitchtubeBots', json.dumps(mongo_bot))
            mongo_bot['list_index'] = list_index
            REDIS.hmset('TwitchtubeBotsById', {mongo_bot['_id']: json.dumps(mongo_bot)})
            return

        cached_bot = json.loads(cached_bot.decode())
        list_index = cached_bot['list_index']
        mongo_bot['active'] = True
        mongo_bot['_id'] = str(mongo_bot['_id'])
        mongo_bot['list_index'] = list_index
        REDIS.hmset('TwitchtubeBotsById', {mongo_bot['_id']: json.dumps(mongo_bot)})
        REDIS.lset('TwitchtubeBots', list_index - 1, json.dumps(mongo_bot))

    if action == 'stop':
        cached_bot = REDIS.hget('TwitchtubeBotsById', bot_id)

        if cached_bot is None:
            return

        cached_bot = json.loads(cached_bot.decode())
        cached_bot['active'] = False
        list_index = cached_bot['list_index']

        REDIS.hmset('TwitchtubeBotsById', {cached_bot['_id']: json.dumps(cached_bot)})
        REDIS.lset('TwitchtubeBots', list_index - 1, json.dumps(cached_bot))

def listen():
    '''Listen to REDIS for bot commands'''
    while 1:
        queue = REDIS.lpop(REDIS_COMMAND_QUEUE)

        if queue is not None:
            action = json.loads(queue.decode())
            bot_id = action['botId']
            action = action['status']
            proccess_command(bot_id, action)

        sleep(.5)

if __name__ == '__main__':
    listen() 

