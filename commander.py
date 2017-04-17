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

        cached_bot = json.loads(cached_bot.decode())
        list_index = cached_bot['list_index']
        mongo_bot['active'] = True
        mongo_bot['_id'] = str(mongo_bot['_id'])
        mongo_bot['list_index'] = list_index
        REDIS.hmset('TwitchtubeBotsById', {mongo_bot['_id']: json.dumps(mongo_bot)})
        REDIS.lset('TwitchtubeBots', list_index - 1, json.dumps(mongo_bot))
        click.echo("Started with update!")

    if action == 'stop':
        cached_bot = REDIS.hget('TwitchtubeBotsById', bot)

        if cached_bot is None:
            click.echo('Bot not found')
            return

        cached_bot = json.loads(cached_bot.decode())
        cached_bot['active'] = False
        list_index = cached_bot['list_index']

        REDIS.hmset('TwitchtubeBotsById', {cached_bot['_id']: json.dumps(cached_bot)})
        REDIS.lset('TwitchtubeBots', list_index - 1, json.dumps(cached_bot))
        click.echo("Stopped")

if __name__ == '__main__':
    twitchtube()
