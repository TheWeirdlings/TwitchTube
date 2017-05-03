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

        command = '!command'
        command_response = 'my response'
        username = 'example-username'
        bot_id = ObjectId()

        DATABASE.commands.insert({
            'botId': bot_id,
            'command': command,
            'message': command_response
        })

        command_manager = CommandManager(DATABASE)
        message = command_manager.check_for_commands(command, username, str(bot_id))

        self.assertEqual(message, command_response)

    def test_returns_message_for_alias(self):
        '''Returns a message for a command alias'''

        command = '!command'
        alias = '!alia'
        command_response = 'my response'
        username = 'example-username'
        bot_id = ObjectId()

        DATABASE.commands.insert({
            'botId': bot_id,
            'command': command,
            'message': command_response,
            'alias': [alias]
        })

        command_manager = CommandManager(DATABASE)
        message = command_manager.check_for_commands(alias, username, str(bot_id))

        self.assertEqual(message, command_response)

    def test_erturns_none_with_incorrect_platform(self):
        '''Ensures that the command manager
        fitlers comamnds by platform if specified'''

        command = '!command'
        command_response = 'my response'
        username = 'example-username'
        platform = 'twitch'
        bot_id = ObjectId()

        DATABASE.commands.insert({
            'botId': bot_id,
            'command': command,
            'message': command_response,
            'platform': 'youtube'
        })

        command_manager = CommandManager(DATABASE, platform)
        message = command_manager.check_for_commands(command, username, str(bot_id))

        self.assertEqual(message, None)

    def test_uses_platform_specific_commands(self):
        '''Ensures that the command manager
        fitlers comamnds by platform if specified'''

        command = '!command'
        command_response = 'my response'
        username = 'example-username'
        platform = 'twitch'
        bot_id = ObjectId()

        DATABASE.commands.insert({
            'botId': bot_id,
            'command': command,
            'message': command_response,
            'platform': 'twitch'
        })

        command_manager = CommandManager(DATABASE, platform)
        message = command_manager.check_for_commands(command, username, str(bot_id))

        self.assertEqual(message, command_response)
