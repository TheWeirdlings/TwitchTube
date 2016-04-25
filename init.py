import socket, string
from time import sleep
import datetime
import threading
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import sys

# reload(sys)
# sys.setdefaultencoding('UTF8')

#localfiles
from twitchtube.twitch import twitchConfig
from twitchtube.twitch.twitchChatSaver import TwitchChatSaver
from twitchtube.twitch.youtubeToTwitch import YouTubeToTwitch
from twitchtube.youtube.twitch_to_youtube import TwitchToYouTube
from twitchtube.youtube.save_youtube_chat import YouTubeChatSaver
from youtubelivestreaming.live_broadcasts import get_live_broadcasts
#endlocalfiles

import httplib2

sys.path.insert(1, '/Library/Python/2.7/site-packages')

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

def get_authenticated_service(args):
    CLIENT_SECRETS_FILE = "./client_secrets.json"

    YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    MISSING_CLIENT_SECRETS_MESSAGE = """
    WARNING: Please configure OAuth 2.0

    To make this sample run you will need to populate the client_secrets.json file
    found at:

       %s

    with information from the Developers Console
    https://console.developers.google.com/

    For more information about the client_secrets.json file format, please visit:
    https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    """ % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       CLIENT_SECRETS_FILE))

    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
        scope=YOUTUBE_READONLY_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))

def startUp(bot, youtube, youtube2):
    #We will share a Twitch socket. But, we still need two programs
    socketToPass = socket.socket()
    socketToPass.connect((twitchConfig.HOST, twitchConfig.PORT))
    socketToPass.send("PASS " + twitchConfig.PASS + "\r\n")
    socketToPass.send("NICK " + twitchConfig.NICK + "\r\n")
    socketToPass.send("JOIN #" + bot['twitch'] + " \r\n")

    run_event = threading.Event()
    run_event.set()

    threads = []

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

def checkProcessFile():
    #TODO: This was the Google way of getting the arguments..
    argparser.add_argument('--botId', help='Bot ID')
    args = argparser.parse_args()
    youtube = get_authenticated_service(args)
    # make a secon service because we techinally have two bots
    youtube2 = get_authenticated_service(args)

    client = MongoClient('mongodb://localhost:27017/')
    db = client.twitchtube

    bot = db.twitchtubeBots.find_one({ '_id': ObjectId(args.botId)})

    #Create a lock for this chat
    pid = str(os.getpid())
    pidfile = "tmp/" + str(bot['_id']) + ".txt"

    if os.path.isfile(pidfile):
        print "%s already exists, exiting" % pidfile
        sys.exit()
    else:
        file(pidfile, 'w').write(pid + "\n\r")

    startUp(bot, youtube, youtube2)

# if __name__ == "__main__":
checkProcessFile()
