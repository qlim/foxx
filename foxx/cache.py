import hashlib
import os
from os import path
from StringIO import StringIO
from time import time
from foxx import settings

class PermissionError(Exception): pass

class FileCache(object):
    def __init__(self, basedir, timeout=300, stable_timeout=60*60*24*14):
        self.basedir = basedir
        self.timeout = timeout
        self.stable_timeout = stable_timeout
        if not path.exists(basedir):
            try:
                os.mkdir(basedir)
            except OSError:
                raise PermissionError, "Could not make cache directory"

        if not os.access(basedir, os.R_OK|os.W_OK):
            raise PermissionError, "Don't have appropriate permissions"

    def getPath(self, url):
        name = hashlib.sha1(url).hexdigest()
        return path.join(self.basedir, name)

    def has(self, url, dynamic=True):
        if path.exists(self.getPath(url)):
            return not self.isStale(url, dynamic)
        return False

    def get(self, url):
        path = self.getPath(url)
        return open(path).read()

    def isStale(self, url, dynamic=True):
        diff = time() - path.getctime(self.getPath(url))
        return diff > (dynamic and self.timeout or self.stable_timeout)

    def set(self, url, txt):
        fout = open(self.getPath(url), 'w')
        fout.write(txt)
        return txt

class NullCache(object):
    def has(self, url):
        return False

    def set(self, url, file):
        return file

def getCache():
    timeout = getattr(settings, 'CACHE_TIMEOUT', 300)
    stable_timeout = getattr(settings, 'CACHE_STABLE_TIMEOUT', 3600*24*14)
    if hasattr(settings, 'CACHE_DIR'):
        try:
            return FileCache(settings.CACHE_DIR, timeout=timeout, stable_timeout=stable_timeout)
        except PermissionError:
            pass
    return NullCache()

DefaultCache = getCache()