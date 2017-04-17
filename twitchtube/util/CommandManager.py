'''Process text to returns command actions'''
from pymongo import MongoClient
from bson.objectid import ObjectId

import config
MONGO = MongoClient(config.mongoUrl)
DATABASE = MONGO[config.database]

class CommandManager(object):
    '''Process text to returns command actions'''
    def __init__(self):
        self.command_cache = {}

    def check_for_commands(self, message, username, bot_id, update=False):
        '''Checks if messgage is a command'''

        if bot_id not in self.command_cache or update:
            self.command_cache[bot_id] = DATABASE.commands.find({"botId": ObjectId(bot_id)})

        if username is 'twitchtube':
            return

        for command in self.command_cache[bot_id]:
            # @TODO: Can we just use a hash here?
            if command['command'] == message:
                return command['message']

        self.command_cache[bot_id].rewind()
