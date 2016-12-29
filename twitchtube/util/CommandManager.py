from bson.objectid import ObjectId

class CommandManager(object):
    def __init__(self, db, bot):
        self.commands = db.commands.find({"botId": bot['_id']})

    def checkForCommands(self, message, username):
        if(username == 'twitchtube'):
            return

        for command in self.commands:
            # @TODO: Can we just use a hash here?
            if (command['command'] == message):
                return command['message']

        self.commands.rewind()
