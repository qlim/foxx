from urllib2 import urlopen
from foxx import settings
from foxx.cache import DefaultCache

class Agent(object):
    def __init__(self, cache=DefaultCache):
        self.cache = cache

    def fetch(self, url, force=False, dynamic=True):
        if self.cache.has(url, dynamic):
            return self.cache.get(url)

        return self.cache.set(url, urlopen(url).read())
