import redis
# r = redis.StrictRedis()

import config
r = redis.from_url(config.redisURL)

class EmojiAssigner(object):
    def __init__(self, bot):
        self.emojiIndex = 0;

        # savedIndex = r.get('emojiIndex')

        self.emojis = [u'🍄', u'🍕', u'🍪', u'🎨', u'🐌', u'🐦', u'🐶',
                 u'👽', u'💀', u'💎', u'💜', u'💩', u'💰', u'🔮',
                 u'🙃', u'🚀', u'🤑', u'🦀', u'🦄']
        print("Emojing")

    def getEmojiForUser(self, username):
        emoji = r.hget("user-eomji", username)
        if (emoji is not None):
            return emoji.decode()

        emoji = self.emojis[self.emojiIndex]
        r.hset("user-eomji", username, emoji.encode("utf-8"))
        self.emojiIndex += 1;
        return emoji;
