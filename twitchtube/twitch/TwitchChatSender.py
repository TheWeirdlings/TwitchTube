import socket, string
from time import sleep
import datetime
import pytz
from dateutil import parser
from bson.objectid import ObjectId
import json
import requests

import twitchConfig
from TwitchPythonApi.twitch_api import TwitchApi
from userActionsManager import UserActionsManager

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

#   This class grabs and chats that are queued for twitch and send them to the twitch channel associated with the bot
#   This is a worker that listens to a queue

class TwitchChatSender(object):
    def __init__(self, inSocket, run_event, bot):
        self.subscribers = []

        self.CHANNEL = '#' + bot['twitch']
        self.s = inSocket
        self.run_event = run_event
        self.bot = bot
        self.setUpTimers()

        self.twitchChannel = self.bot['twitch']
        self.twitchApi = TwitchApi()
        self.twitchFollowerCursor = None
        self.lastMinuteCheckedForFollowers = None
        self.lastTimeFollowerAlerted = None

        #Subscribers should register outside of this scope
        self.usersActionsManager = UserActionsManager(self.s, self.bot)
        self.register(self.usersActionsManager)

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def notifySubscribers(self):
        for subscriber in self.subscribers:
            subscriber.exectute()

    def setUpTimers(self):
        timers = db.timers.find({"botId": str(ObjectId(self.bot['_id'])) })

        #Timers are in the seciton because we need a program that polls the time
        self.timers = {}

        for timer in timers:
            interval = int(timer['interval'])

            while interval <= 60:
                if interval not in self.timers:
                    self.timers[interval] = []
                self.timers[interval].append(timer['message'])
                interval += interval

        now = datetime.datetime.now()
        self.lastMinuteCheckedForTimers = now.minute

    def sendTimers(self):
        now = datetime.datetime.now()
        currentMinute = now.minute

        if currentMinute != self.lastMinuteCheckedForTimers:
            self.lastMinuteCheckedForTimers = currentMinute
            if currentMinute == 0:
                currentMinute = 60
            if currentMinute in self.timers:
                for timerMessage in self.timers[currentMinute]:
                    self.sendTwitchMessge(timerMessage)

    def sendTwitchMessge(self, message):
        try:
            self.s.send("PRIVMSG " + self.CHANNEL + " :" + message + "\r\n")
        except UnicodeDecodeError:
            print 'Add support'

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

    def sendYoutubeChatToTwitch(self):
        while self.run_event.is_set():
            prevMessage = ""
            chatToSend = TwitchMessageFromYouTube(self.bot)
            chatToSend.getNextMessageToSend()

            self.sendTimers()

            if 'twitchOptions' in self.bot and self.bot['twitchOptions']['displayTwitchAlerts'] == True:
                self.checkForNewFollower()

            self.notifySubscribers()

            if chatToSend.mongoDocument is not None:
                if ("(From Twitch)" in chatToSend.mongoDocument['message']) or (chatToSend.mongoDocument['message'] == prevMessage):
                    chatToSend.markSent();
                    prevMessage = ""
                else:
                    prevMessage = chatToSend.mongoDocument['message']
                    self.sendTwitchMessge(chatToSend.mongoDocument['message'])
                    chatToSend.markSent();
            sleep(1.5)
