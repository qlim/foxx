from django.utils import feedgenerator
from foxx.agent import Agent
from foxx.cache import DefaultCache as cache
from xml.dom import minidom
from lxml import etree
from BeautifulSoup import BeautifulSoup
from datetime import datetime
import email, time, pytz

s = lambda x: ''.join(x)

def convert_date(d):
    utctimestamp = email.Utils.mktime_tz(email.Utils.parsedate_tz(d))
    utcdate = datetime.fromtimestamp(utctimestamp, pytz.utc)
    return utcdate


class FreakonomicsParser(object):
    URL = u"http://feedproxy.google.com/freakonomicsblog"

    def __init__(self):
        self.agent = Agent()

    def fetch_url(self):
        return self.agent.fetch(self.URL)

    def parse(self):
        tree = etree.fromstring(self.fetch_url(), base_url=self.URL)

        self.f = feedgenerator.Atom1Feed(
            title=s(tree.xpath('/rss/channel/title/text()')),
            link=s(tree.xpath('/rss/channel/link/text()')),
            description=s(tree.xpath('/rss/channel/description/text()')),
            language=s(tree.xpath('/rss/channel/language/text()')))

        for item in tree.xpath('/rss/channel/item'):
            self.parse_item(item)

        return self.f

    def parse_item(self, item):
        n = {'feedburner':'http://rssnamespace.org/feedburner/ext/1.0',
             'dc': 'http://purl.org/dc/elements/1.1/'}

        title = s(item.xpath('title/text()'))
        link = s(item.xpath('feedburner:origLink/text()', namespaces=n))
        pubdate = convert_date(s(item.xpath('pubDate/text()')))
        author_name = s(item.xpath('dc:creator/text()', namespaces=n))
        categories = item.xpath('category/text()')

        if cache.has(link+"#description", dynamic=False):
            description = cache.get(link+"#description")
        else:
            soup = BeautifulSoup(self.agent.fetch(link))
            div = soup.find('div', {'class': 'entry-content'})
            description = div.prettify()
            cache.set(link+"#description", description)

        self.f.add_item(title, link, description, author_name=author_name,
            pubdate=pubdate, categories=categories)

def main():
    fp = FreakonomicsParser()
    feed = fp.parse()
    #print feed.writeString('UTF-8')

def prof():
    import hotshot
    prof = hotshot.Profile('hp')
    prof.runcall(main)
    prof.close()

    from hotshot import stats
    s = stats.load('hp')
    print s.sort_stats('time').print_stats()

if __name__ == '__main__':

    #prof()
    main()