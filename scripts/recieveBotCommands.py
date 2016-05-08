#!/usr/bin/env python
import pika
import json
import os
import signal

# abspath = os.path.abspath(__file__)
# dname = os.path.dirname(abspath)
# os.chdir(dname)
workingDirectory = os.getcwd();

import config
queueName = config.rabbitQueue

def getPidForBot(botId):
    pid = None
    filename = "tmp/" + botId + ".txt"
    try:
        with open(filename) as pidFile:
            pid = pidFile.readlines()
            pid = int(pid[0])
    except:
        print "No process"

    return pid

def stopBot(pid, filename, botId):
    try:
        os.kill(pid, signal.SIGTERM)
    except:
        print("Error")

    try:
        os.remove(filename)
    except:
        print("Error")
    print ("stoping %s" % botId)

def applyActionToBot(botId, action, pid):
    startScript = "python init.py --botId={BotId} > tmp/logs-{BotId}.txt 2>&1 &"
    filename = "tmp/" + botId + ".txt"

    botStartScript = startScript.replace("{BotId}", str(botId))

    if action == "start":
        if pid is not None:
            print "Cannot start"
            return

        os.system(botStartScript)
        print ("starting %s" % botId)

    elif action == "restart":
        if pid is None:
            print "Cannot restart"
            return

        stopBot(pid, filename, botId)
        os.system(botStartScript)

        print ("restarted %s" % botId)

    elif action == "stop":
        if pid is None:
            print "Cannot stop"
            return

        stopBot(pid, filename, botId)

        print ("stoping %s" % botId)


def callback(ch, method, properties, body):
    command = json.loads(body)
    botId = command['botId']
    action = command['status']

    pid = getPidForBot(botId)

    applyActionToBot(botId, action, pid)

    print(" [x] Received %r" % command)

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()
channel.queue_declare(queue=queueName)
channel.basic_consume(callback,
                      queue=queueName,
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
