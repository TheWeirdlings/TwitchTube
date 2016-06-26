import socket, string
from time import sleep
import datetime
import threading
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import sys
import httplib2
from oauth2client.tools import argparser, run_flow
import logging

# reload(sys)
# sys.setdefaultencoding('UTF8')

#localfiles
import config
from twitchtube.twitch import twitchConfig
from twitchtube.twitch.twitchChatSaver import TwitchChatSaver
from twitchtube.twitch.youtubeToTwitch import YouTubeToTwitch
from twitchtube.youtube.twitch_to_youtube import TwitchToYouTube
from twitchtube.youtube.save_youtube_chat import YouTubeChatSaver
from youtubelivestreaming.live_broadcasts import get_live_broadcasts
from helpers import get_authenticated_service
#endlocalfiles


def startUp(bot, youtube, youtube2):
    #We will share a Twitch socket. But, we still need two programs
    if ('twitch' in bot) and (bot['twitch'] is not None):
        socketToPass = socket.socket()
        socketToPass.connect((twitchConfig.HOST, twitchConfig.PORT))
        socketToPass.send("PASS " + twitchConfig.PASS + "\r\n")
        socketToPass.send("NICK " + twitchConfig.NICK + "\r\n")
        socketToPass.send("JOIN #" + bot['twitch'] + " \r\n")

    run_event = threading.Event()
    run_event.set()

    threads = []

    if ('twitch' in bot) and (bot['twitch'] is not None):
        ts = TwitchChatSaver(socketToPass, bot)
        thread = threading.Thread(target=ts.start, args=(run_event,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

        tubeToTwitch = YouTubeToTwitch(socketToPass,run_event,bot)
        thread = threading.Thread(target=tubeToTwitch.sendYoutubeChatToTwitch, args=())
        thread.daemon = True
        thread.start()
        threads.append(thread)

    if ('youtube' in bot) and (bot['youtube'] is not None):
        twitchToYoutube = TwitchToYouTube(bot, youtube)
        thread = threading.Thread(target=twitchToYoutube.run, args=(run_event,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

        ytcs = YouTubeChatSaver(bot, youtube2)
        thread = threading.Thread(target=ytcs.run, args=(run_event,))
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

    client = MongoClient('mongodb://localhost:27017/')
    db = client[config.database]

    bot = db.twitchtubeBots.find_one({ '_id': ObjectId(args.botId)})

    #Create a lock for this chat
    pid = str(os.getpid())
    pidfile = "tmp/" + str(bot['_id']) + ".txt"

    #Set up logging
    logfile = "tmp/" + str(bot['_id']) + "-logfile.txt"
    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logging.debug('Log file is good.')

    # Install exception handler
    sys.excepthook = uncaught_exception_handler

    if os.path.isfile(pidfile):
        print "%s already exists, exiting" % pidfile
        sys.exit()
    else:
        file(pidfile, 'w').write(pid + "\n\r")

    db.twitchtubeBots.update({ '_id': ObjectId(args.botId)}, {'$set': {'status': "running"}});
    startUp(bot, youtube, youtube2)

# if __name__ == "__main__":
checkProcessFile()
