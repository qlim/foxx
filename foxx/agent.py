from urllib2 import urlopen

class Agent(object):
    def fetch(self, url):
        return urlopen(url)
