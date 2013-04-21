import sys
import os

import requests
from BeautifulSoup import BeautifulSoup


class URLParse(object):
    """ parse url, simply update parameter. """
    def __init__(self, url):
        """
        example: url='http://asd.com?a=1&b=2' then
                 query='http://asd.com'
                 params='a=1&b=2'
                 pairs={'a':'1','b':'2'}
        Converting to the dictionary Used for remove duplicate.
        """
        if '?' in url:
            self.query, self.params = url.split('?', 1)
        else:
            self.query = url
            self.params = ''
        self.pairs = {}
        if self.params:
            self.pairs = dict(i.split('=', 1) for i in self.params.split('&'))

    def update_params(self, new_params):
        """
        :param new_params: like ['a=2', 'b=4', 'qww=3']
        """
        temp = dict(i.split('=') for i in new_params)
        self.pairs.update(temp)
        self.params = '&'.join('%s=%s' % (k, v) for k, v in self.pairs.items())

    def get_url(self):
        """
        :return: the whole url
        """
        return '%s?%s' % (self.query, self.params)


class Crawler(object):
    def __init__(self, url):
        """
        :param url: url to Crawling
        """
        html = requests.get(url).content.decode('GB18030')
        self.soup = BeautifulSoup(html)
        self.params = []

    def update(self, tag, select, params):
        """
        :param tag: tag to change, like 'a'.
        :param select: attribute filter to tag, like {'href': True}.
        :param params: like ['a = 1', 'b = 2', 'c = 3'].
        example: http://asd.com?ldd=1&a=4  then:
                 http://asd.com?ldd=1&a=1&b=2&c=3
        """
        tags = self.soup.findAll(tag, attrs=select)
        self.params = params
        map(self._update, tags)

    def _update(self, tag):
        urlparse = URLParse(tag['href'])
        if tag.find('img') is not None:
            param_ = self.params
        else:
            param_ = self.params[0:2]
        urlparse.update_params(param_)
        tag['href'] = urlparse.get_url()

    def save(self, path='/tmp/', name='index.html'):
        if not os.path.exists(path):
            os.makedirs(path)
        fp = open('%s%s' % (path, name), 'w')
        fp.write(str(self.soup))
        fp.close()


def main():
    url = sys.argv[1]
    params = sys.argv[2:]
    crawler = Crawler(url)
    crawler.update('a', {'href': True}, params)
    crawler.save()


if __name__ == '__main__':
    main()
