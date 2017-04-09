# The Twitch Workers
Twitchtube works be create several twitch workers that will watch
all active channels. 

## The start stream watcher
These workers will monitor channels to see when they go live, if they go live,
the work will send an active notice to the twitch queue

Process:
  1. Grab all bots with watch option
  2. Query the twitch api to check if online
  3. If online, send notice to Redis


## The command watcher
These workers listen to the TwitchtubeCommand Redis queue and allow for users
to start, stop, restart, etc their bot from several UIs


## The Twitch Chat Savers
These workers will create a socket connection the Twitch IRC and save messages
that come into the channels

Process:
  1. Grab bots from Redis TwitchtubeBots list starting from their
    offset to their max number of channels
  2. Iterate through bots and grab all the channels from bots that are active
  3. Listen to active chats and save incomming
  4. Check for new active bots
  5. If new actives, send connection to active bots