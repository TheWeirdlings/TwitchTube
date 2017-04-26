'''Process text to returns command actions'''
from pymongo import MongoClient
from bson.objectid import ObjectId

# @TODO: inject db
import config
MONGO = MongoClient(config.mongoUrl)
DATABASE = MONGO[config.database]

class CommandManager(object):
    '''Process text to returns command actions'''
    def __init__(self, db=None):
        self.command_cache = {}
        self.database = DATABASE
        if db is not None:
            self.database = db

    def command_is_alias(self, command_from_db, message):
        '''Check if message is an alias'''
        alias_prop = 'alias' in command_from_db
        return alias_prop and message in command_from_db['alias']

    def check_for_commands(self, message, username, bot_id, update=False):
        '''Checks if messgage is a command'''

        if bot_id not in self.command_cache or update:
            self.command_cache[bot_id] = self.database.commands.find({"botId": ObjectId(bot_id)})

        if username is 'twitchtube':
            return

        for command in self.command_cache[bot_id]:
            # @TODO: Can we just use a hash here?
            if command['command'] == message or self.command_is_alias(command, message):
                return command['message']

        self.command_cache[bot_id].rewind()
