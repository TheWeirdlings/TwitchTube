#!/usr/bin/env python
import json
import os
import signal
from time import sleep

# abspath = os.path.abspath(__file__)
# dname = os.path.dirname(abspath)
# os.chdir(dname)
workingDirectory = os.getcwd();

import config
queueName = config.rabbitQueue

import redis
r = redis.StrictRedis()
reddisBotCommandQueue = config.reddisBotCommandQueue

def applyActionToBot(botId, action):
    if action == 'start':
        startScript = "pm2 {Action} --name={BotId} init.py -- --botId={BotId}"
    else:
        startScript = "pm2 {Action} {BotId}"
    botStartScript = startScript.replace("{Action}", str(action)).replace("{BotId}", str(botId))
    os.system(botStartScript)

while 1:
    queue = r.lpop(reddisBotCommandQueue)

    if queue is not None:
        command = json.loads(queue.decode())
        botId = command['botId']
        action = command['status']
        applyActionToBot(botId, action)

    sleep(.5)
