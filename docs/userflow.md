# User Flow
The expected flow starting from the user's perspective
with technicall descriptions is as follows:

## Starting
  1. User signs in to Twitchtube.io
  2. User links both Twtich and Youtube
  3. User hits start button
  4. CommandWorker listens for start command
  5. CommandWorker finds bot in Mongodb
  6. CommandWorker creates entry in TwtichtubeBots for new bot and sets to active
  7. CommandWorker creates entry in TwitchtubeBotsHashedById and sets index in TwitchtubeBots 
  for Youtube Sender (this most effiecient bot) and Stoping with CommandWorker (See below)

## Stopping
  1. User hits stop button
  2. CommandWorker finds entry in TwitchtubeBotsHashedById, grabs index
  then finds bot in TwitchtubeBots
  3. CommandWorker sets bot to inactive in both sets

## Restarting
  1. User hits restart button
  2. CommandWorker finds entry in TwitchtubeBotsHashedById, grabs index
  then finds bot in TwitchtubeBots
  3. CommandWorker updates bot info in both sets