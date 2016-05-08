import json
import os
import signal
from pymongo import MongoClient

import config
client = MongoClient('mongodb://localhost:27017/')
db = client[config.database]
bots = db.twitchtubeBots

startScript = "nohup python ../bot2.py {BotId} > ../logs.txt &"
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#TODO: How do we auth with Twitch
#TODO: How to we use multiple Youtube acconts?

def manageBot(bot):
    status = bot['status']
    twitch = bot['twitch']

    botStartScript = startScript.replace("{BotId}", str(bot['_id']))

    #get processid
    pid = ""
    filename = "../tmp/"+twitch+".txt"
    try:
        with open(filename) as pidFile:
            pid = pidFile.readlines()
            pid = int(pid[0])
    except:
        print "No process"

    if status == 'running':
        if pid == "":
            os.system(botStartScript)
            print botStartScript
            print "Starting from no process"
        else:
            try:
                #Check for process
                os.kill(pid, 0)
                print "Already running"
            except:
                #Start Script
                os.remove(filename)
                os.system(botStartScript)
                print "Starting"

    if status == 'restart' or status == 'start':
        if pid != "":
            print "Restarting"
            try:
                os.kill(pid, signal.SIGTERM)
                os.remove(filename)
            except:
                os.remove(filename)
            os.system(botStartScript)
        else:
            if os.path.isfile(filename):
                os.remove(filename)
            os.system(botStartScript)
            print "Not running, will start"

        bots.update({'_id': bot['_id']}, {'$set': {'status': 'running'}})

    if status == 'stop':
        if pid != "":
            print "Stopping"
            os.kill(pid, signal.SIGTERM)
        else:
            print "Not running"

# botsFile = "./scripts/botsInfo.json"
# #Check for entry in mongo
# with open(botsFile) as botsData:
#     bots = json.load(botsData)
#     for bot in bots:
#         manageBot(bot)

for bot in bots.find():
    manageBot(bot)
