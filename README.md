About
=========
TwitchTube [twitchtube.io](http://twitchtube.io) is an open source streaming bot for Twitch and Youtube.  The bot's main purpose is to synchronize chat between Youtube and Twitch, but contains many regular bot features as well. The following features are:

1. Chat Sync between Twitch and Youtube
2. Commands
3. Timers
4. Self hosting
5. Emoji Assignment to Users

We add features every week, so feel free to open an issue request here or contact us on [twitchtube.io](http://twitchtube.io).

The bot can be self-hosted, but we are currently taking beta users for our web/mobile apps. Feel free to sign up on our webpage: [twitchtube.io Beta Signup](http://twitchtube.io/beta)

To Set up
=========

Clone
---------------------
* git clone https://github.com/TheWeirdlings/TwitchTube.git
* or Fork :)

Configure
---------------------
1. Set Up a Python Virtual environment (@TODO: docs)
2. pip install -r requirements.txt
3. Intsall twitchtube `pip install -e .`

Connect Youtube
---------------------
1. Go to https://console.developers.google.com
2. Create a new project or use an existing
3. Search for YouTube Data API v3 and enable the api
4. Select Credentials on the left hand side
5. Click create credentials, then click OAuth
6. Under application type select Other, then click create
7. Download the Json file, and rename the file to client_secrets.json
8. Copy the client_secrets.json to the root directory of twitchtube
9. Now, when you first run any Youtube worker or generator.py you will need to add the --noauth_local_webserver flag.     Examples are below

Connect Twitch
---------------------
1. Copy twitchtube/twitch/twitchConfig-example.py to twitchtube/twitch/twitchConfig.py
2. Get an OAuth password from (http://www.twitchapps.com/tmi/). Use the NICK that you register
3. Fill out the twitch config with your developer information.

Add a bot to your mongo database
---------------------
1. Start mongo with the mongod command
2. python generator.py --action=create --item=bot or python generator.py --action=create --item=bot --noauth_local_webserver for your first run
3. python generator.py --action=read --item=bot
* (Copy the bot id)

Run the Workers
---------------------
- python workers/TwitchChatSaverWorker.py
- python workers/TwitchChatSenderWorker.py
- python workers/YoutubeSaverWorker.py
- python workers/YoutubeSenderWorker.py
- python workers/CommandListener.py (if you want the UI commands)

Server Set Up
---------------------
1. Install Redis https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04
2. Install mongo
3. Install nodejs https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-an-ubuntu-14-04-server
4. Install pm2 - npm isntall -g pm2
5. python commander.py --bot=[bot_id] --action=start

# Runnings tests
 - pip install pytest
 - pytest
 - pytest --cov-report html --cov=twitchtube tests/
