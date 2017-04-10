'''A CLI to manage Twitchtube'''
import click
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

import redis

import config
CLINET = MongoClient(config.mongoUrl)
DB = CLINET[config.database]
REDIS = redis.from_url(config.redisURL)

@click.command()
@click.option('--bot', default='', help='The id of the bot to manage.')
@click.option('--action', default='', help='The action to commit (start, stop or restart)')
def twitchtube(bot, action):
    '''A CLI to manage Twitchtube'''
    if action == 'start':
        mongo_bot = DB.twitchtubeBots.find_one({'_id': ObjectId(bot)})

        if mongo_bot is None:
            click.echo('Bot not found')
            return

        cached_bot = REDIS.hget('TwitchtubeBotsById', bot)

        mongo_bot['active'] = True
        mongo_bot['_id'] = str(mongo_bot['_id'])

        if cached_bot is None:
            list_index = REDIS.lpush('TwitchtubeBots', json.dumps(mongo_bot))
            mongo_bot['list_index'] = list_index
            REDIS.hmset('TwitchtubeBotsById', {mongo_bot['_id']: json.dumps(mongo_bot)})
            click.echo("Started!")
            return

        # @TODO: Update bot if exists


if __name__ == '__main__':
    twitchtube()
