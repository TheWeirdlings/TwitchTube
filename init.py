import socket
from time import sleep
import threading
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import sys
from oauth2client.tools import argparser
import logging

#localfiles
import config
from twitchtube.twitch.TwitchChatSaver import TwitchChatSaver
from twitchtube.twitch.TwitchChatSender import TwitchChatSender

from twitchtube.youtube.YoutubeChatSender import YoutubeChatSender
from twitchtube.youtube.YoutubeChatSaver import YoutubeChatSaver
from twitchtube.youtube.YoutubePointManager import YoutubePointManager

from youtubelivestreaming.live_broadcasts import get_live_broadcasts
from helpers import get_authenticated_service
#endlocalfiles

def startUp(bot, youtube, youtube2):
    #We will share a Twitch socket. But, we still need two programs
    if ('twitch' in bot) and (bot['twitch'] is not None):
        socketToPass = socket.socket()
        socketToPass.connect((config.HOST, config.PORT))

        ircPass = "PASS " + config.PASS + "\r\n"
        socketToPass.send(ircPass.encode('utf-8'))

        ircNick = "NICK " + config.NICK + "\r\n"
        socketToPass.send(ircNick.encode('utf-8'))

        # ircUser = 'USER ' + config.NICK + ' 0 * :' + config.USER + '\r\n'
        # socketToPass.send(ircUser.encode('utf-8'))

        ircSend = "JOIN #" + bot['twitch'] + " \r\n"
        socketToPass.send(ircSend.encode('utf-8'))

    run_event = threading.Event()
    run_event.set()

    threads = []

    if ('twitch' in bot) and (bot['twitch'] is not None):
        ts = TwitchChatSaver(socketToPass, bot)
        thread = threading.Thread(target=ts.start, args=(run_event,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

        tubeToTwitch = TwitchChatSender(socketToPass,run_event, bot)
        thread = threading.Thread(target=tubeToTwitch.work, args=())
        thread.daemon = True
        thread.start()
        threads.append(thread)

    if ('youtube' in bot) and (bot['youtube'] is not None):
        # Chat saver
        ytcs = YoutubeChatSaver(bot, youtube2)
        thread = threading.Thread(target=ytcs.run, args=(run_event,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

        # Chat sender
        twitchToYoutube = YoutubeChatSender(bot, youtube)

        # Subs
        # youtubePointManager = YoutubePointManager(youtube)
        # twitchToYoutube.register(youtubePointManager)

        thread = threading.Thread(target=twitchToYoutube.run, args=(run_event,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    try:
        while 1:
            sleep(.1)

    except KeyboardInterrupt:
        run_event.clear()

def uncaught_exception_handler(type, value, tb):
    logging.exception("Uncaught exception: {0}".format(str(value)))

def checkProcessFile():
    #TODO: This was the Google way of getting the arguments..
    argparser.add_argument('--botId', help='Bot ID')
    args = argparser.parse_args()
    youtube = get_authenticated_service(args)
    # make a secon service because we techinally have two bots
    youtube2 = get_authenticated_service(args)

    client = MongoClient(config.mongoUrl)
    db = client[config.database]

    bot = db.twitchtubeBots.find_one({ '_id': ObjectId(args.botId)})

    db.twitchtubeBots.update({ '_id': ObjectId(args.botId)}, {'$set': {'status': "running"}});
    startUp(bot, youtube, youtube2)

if __name__ == "__main__":
    checkProcessFile()
