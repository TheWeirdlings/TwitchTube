'''Manages the colleciton of message on the
    Redis YoutubeMessageToSync list'''

import redis
import config

class YoutubeMessageCollection(object):
    '''Manages the colleciton of message on the
    Redis YoutubeMessageToSync list'''
    def __init__(self):
        self.redis = redis.from_url(config.redisURL)
        # self.bot = bot
        # self.botId = self.bot['_id'];

    def get_next_message_to_send(self):
        '''Grabs next message on the redis queue'''
        return self.redis.lpop("YoutubeMessageToSync")
