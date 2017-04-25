"""Tests for CommandManager."""
import unittest
from pymongo import MongoClient
from bson.objectid import ObjectId

from twitchtube.util.CommandManager import CommandManager

import config
MONGO = MongoClient(config.mongoUrl)
DATABASE = MONGO[config.database_test]

class CommandManagerTestCase(unittest.TestCase):
    """Tests for CommandManager."""

    def tearDown(self):
        DATABASE.commands.remove({})

    def test_check_for_commands(self):
        '''Checks to ensure a message is returned
        if a comamnd is sent'''

        message = '!command'
        command_response = 'my response'
        username = 'example-username'
        bot_id = ObjectId()

        DATABASE.commands.insert({
            'botId': bot_id,
            'command': message,
            'message': command_response
        })

        command_manager = CommandManager(DATABASE)
        message = command_manager.check_for_commands(message, username, str(bot_id))

        self.assertEqual(message, command_response)
