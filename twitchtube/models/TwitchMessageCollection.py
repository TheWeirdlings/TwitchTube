'''Manages the colleciton of message on the
    Redis TwitchMessageToSync list'''
import redis
import config

class TwitchMessageCollection(object):
    '''Manages the colleciton of message on the
    Redis TwitchMessageToSync list'''
    def __init__(self):
        self.redis = redis.from_url(config.redisURL)

    def get_next_message_to_send(self):
        '''Gets next message on the redis stack'''
        return self.redis.lpop("TwitchMessageToSync")
