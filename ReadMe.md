About
=========
TwitchTube [twitchtube.io](http://twitchtube.io) is an open source streaming bot for Twitch and Youtube.  The bot's main purpose is to synchronize chat between Youtube and Twitch, but contains many regular bot features as well. The following features are:

1. Chat Sync between Twitch and Youtube
2. Commands
3. Timers
4. Self hosting

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
1. ./scripts/config.sh
2. pip install -r requirements.txt

Connect Twitch
---------------------
1. Copy twitchtube/twitch/twitchConfig-example.py to twitchtube/twitch/twitchConfig.py
2. Get an OAuth password from (https://www.twitch.tv/settings/connections). Register an app at the bottom
3. Fill out the twitch config with your developer information.

Add a bot to your mongo database
---------------------
1. Start mongo with the mongod command
2. python generator.py --action=add --item=bot
3. python generator.py --action=read --item=bot
* (Copy the bot id)

Run the script
---------------------
python init.py --botId=[insert-bot-id]
