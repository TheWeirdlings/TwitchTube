import socket
from time import sleep

# Ugly hack to allow absolute import from the root folder
# whatever its name is. Please forgive the heresy.
# if __name__ == "__main__" and __package__ is None:
from sys import path
from os.path import dirname as dir

path.append(dir(path[0]))
__package__ = "examples"

import config
from twitchtube.twitch.TwitchChatSender import TwitchChatSender

#TODO Move to helper?
def connectToTwitch():
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

    return socketToPass

if __name__ == "__main__":
    bot = {
        "twitch": "thehollidayinn",
        "_id": "5853c8142b471021fc94b043",
    }

    socketToPass = connectToTwitch()

    ts = TwitchChatSender(socketToPass, None, bot)

    while True:
        ts.sendMessageFromQueue()
        sleep(1)

    # try:
    #     while 1:
    #         print("SFD")
    #         # ts.readSocket()
    #         sleep(1)
    #
    # except KeyboardInterrupt:
    #     print("Peace!")
