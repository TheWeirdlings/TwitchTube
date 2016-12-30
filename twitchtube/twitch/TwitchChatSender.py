from time import sleep
import datetime
import pytz
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
        # self.setUpTimers()

        self.twitchChannel = self.bot['twitch']
        self.twitchApi = TwitchApi()
        self.twitchFollowerCursor = None
        self.lastMinuteCheckedForFollowers = None
        self.lastTimeFollowerAlerted = None

        #Subscribers should register outside of this scope
        # self.usersActionsManager = UserActionsManager(self.s, self.bot)
        # self.register(self.usersActionsManager)

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def notifySubscribers(self):
        for subscriber in self.subscribers:
            subscriber.exectute()

    def sendTwitchMessge(self, message):
        ircMessage = 'PRIVMSG %s :%s\n' % (self.CHANNEL, message)
        self.s.send(ircMessage.encode('utf-8'))

    def checkForNewFollower(self):
        now = datetime.datetime.now(pytz.UTC)
        currentMinute = now.minute

        if self.lastMinuteCheckedForFollowers is None or currentMinute != self.lastMinuteCheckedForFollowers:
            self.lastMinuteCheckedForFollowers = currentMinute
            followers = self.twitchApi.getFollowers(self.twitchChannel, self.twitchFollowerCursor)
            followers = json.loads(followers)

            if self.lastTimeFollowerAlerted is None:
                if len(followers['follows']) > 0:
                    lastFollower = followers['follows'][0]
                    lastFollowerDate = parser.parse(lastFollower['created_at'])
                    self.lastTimeFollowerAlerted = lastFollowerDate
                else:
                    self.lastTimeFollowerAlerted = now

            for follower in followers['follows']:
                followerDate = parser.parse(follower['created_at'])

                if followerDate > self.lastTimeFollowerAlerted:
                    followerDisplayName = follower['user']['display_name']

                    newFollerMessage = self.bot['twitchOptions']['twitchAlertText']
                    newFollerMessage = newFollerMessage.replace("{{userId}}", followerDisplayName)

                    self.sendTwitchMessge(newFollerMessage)

                lastFollower = followers['follows'][0]
                lastFollowerDate = parser.parse(lastFollower['created_at'])
                self.lastTimeFollowerAlerted = lastFollowerDate

    def sendMessageFromQueue(self):
        twitchCollection = TwitchMessageCollection(self.bot)
        chatToSend = twitchCollection.getNextMessageToSend()

        # if 'twitchOptions' in self.bot and self.bot['twitchOptions']['displayTwitchAlerts'] == True:
        #     self.checkForNewFollower()

        self.notifySubscribers()

        if chatToSend is None:
            return

        chatToSend = json.loads(chatToSend.decode())
        self.sendTwitchMessge(chatToSend['message'])

    def work(self):
        while self.run_event.is_set():
            self.sendMessageFromQueue()
            sleep(1.5)
