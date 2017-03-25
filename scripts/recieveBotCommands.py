#!/usr/bin/env python
import json
import os
import psutil
import signal
from time import sleep

# abspath = os.path.abspath(__file__)
# dname = os.path.dirname(abspath)
# os.chdir(dname)
workingDirectory = os.getcwd();

import config
queueName = config.rabbitQueue

import redis
# r = redis.StrictRedis()
r = redis.from_url(config.redisURL)
reddisBotCommandQueue = config.reddisBotCommandQueue

def applyActionToBot(botId, action):
    if action == 'start':
        startScript = "pm2 {Action} --name={BotId} init.py -- --botId={BotId}"
    else:
        startScript = "pm2 {Action} {BotId}"
    botStartScript = startScript.replace("{Action}", str(action)).replace("{BotId}", str(botId))
    print(botStartScript, flush=True)
    os.system(botStartScript)

def memoryUsageIsBelowThreshold():
    memory = psutil.virtual_memory()
    used = memory[3]
    total = memory[0]
    percentUsed = (used/total) * 100
    return percentUsed < 60

while 1:

    if memoryUsageIsBelowThreshold() == True:
        print("CPU memory usage is too high", flush=True)
        sleep(1)

    else:
        queue = r.lpop(reddisBotCommandQueue)

        if queue is not None:
            command = json.loads(queue.decode())
            botId = command['botId']
            action = command['status']
            applyActionToBot(botId, action)

        sleep(.5)
