from time import sleep
from dateutil import parser
from bson.objectid import ObjectId
import json

from TwitchPythonApi.twitch_api import TwitchApi
from twitchtube.models.TwitchMessageCollection import TwitchMessageCollection

# from userActionsManager import UserActionsManager

#   This class grabs and chats that are queued for twitch and send them to the twitch channel associated with the bot
#   This is a worker that listens to a queue
class TwitchChatSender(object):
    def __init__(self, inSocket, run_event, bot):
        self.subscribers = []

        self.CHANNEL = '#' + bot['twitch']
        self.s = inSocket
        self.run_event = run_event
        self.bot = bot

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def notifySubscribers(self):
        for subscriber in self.subscribers:
            subscriber.exectute()

    def sendTwitchMessge(self, message):
        ircMessage = 'PRIVMSG %s :%s\n' % (self.CHANNEL, message)
        self.s.send(ircMessage.encode('utf-8'))

    def sendMessageFromQueue(self):
        twitchCollection = TwitchMessageCollection(self.bot)
        chatToSend = twitchCollection.getNextMessageToSend()

        if chatToSend is None:
            return

        chatToSend = json.loads(chatToSend.decode())

        if chatToSend['author'] == 'Twitchtube':
            return

        self.sendTwitchMessge(chatToSend['message'])

    def work(self):
        while self.run_event.is_set():
            self.sendMessageFromQueue()
            self.notifySubscribers()
            sleep(1.5)
