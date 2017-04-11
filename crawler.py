'''
a crawler used for parsing pages in wikipedia
'''
import re
import http
from urllib.error import URLError
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from log import debug_log, log
import settings


class Crawler(object):
    '''crawler class
    '''
    def __init__(self, start=None, relurl=None):
        '''`relurl` can be None if the url is not known yet. Crawler
        will automatically generate the url for you.
        start: name of lemma at the starting point
        relurl: @NOTE:RELATIVE url
        '''
        self._start = start
        self._url = self._BASE_RUL + relurl if relurl is not None else None
        if settings.debug:
            debug_log(self._url)

        self._soup = self._make_soup()

    # class varialbes
    _BASE_RUL = 'https://en.wikipedia.org'
    _HEADERS = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

    def has_soup(self):
        '''check if the crawler has a non-empty soup'''
        return self._soup is not None

    def generate_full_url(self):
        '''generate full url of a given relative url.
        O(n) since the encode and decode are linear.
        '''
        url = self._BASE_RUL + '/wiki/' + self._start
        # get rid of non-ascii characters by encode + decode
        url = url.encode('ascii', 'ignore').decode('ascii')
        return url

    def _make_soup(self):
        '''send request, handle response, and get soup object
        @NOTE: It will automatically generate url if url was
        originally passed in as `None`.
        Return:
            soup object if no Exception is raised.
            Otherwise return `None`.
        '''
        try:
            if self._url is None:
                self._url = self.generate_full_url()
                if settings.debug:
                    debug_log('get request...')
                    debug_log('url is {}'.format(self._url))

            req = Request(self._url, headers=self._HEADERS)
            response = urlopen(req)
            soup = BeautifulSoup(response, "html5lib")

        except URLError as e:
            err_msg = 'Cannot open the page with name {}: {}'.format(
                self._start, e)
            if settings.debug:
                debug_log(err_msg)
            log(err_msg)
            return None

        except UnicodeDecodeError as e:
            # example: https://en.wikipedia.org/wiki/Kronkåsa
            # 'Kronkåsa' contains non-ascii characters
            # We don't do encode & decode trick simply because it will
            # not be a reasonable keyword to search.
            err_msg = 'Cannot open the page with name {}: {}'.format(
                self._start, e)
            if settings.debug:
                debug_log(err_msg)
            log(err_msg)
            return None

        except http.client.BadStatusLine as e:
            err_msg = 'Cannot open the page with name {}: {}'.format(
                self._start, e)
            if settings.debug:
                debug_log(err_msg)
            log(err_msg)
            return None

        else:
            return soup

    def get_all_links(self):
        '''get all the links in one page, aka get all edges of one node
        Return: a list of tuples that the first element is the number of
        links, the second element is the name and
        the third element its the RELATIVE url.
        O(n) where n is approximately the size of the HTML tree.
        '''
        assert self.has_soup(), 'self._soup is None'

        # valid urls need to be in this format: start with /wiki/ and
        # not contain `:`.
        all_link_tags = self._soup.find(id='bodyContent')\
                            .find_all('a',
                                      href=re.compile('^(/wiki/)((?!:).)*$'))
        # invalid: aaa/wiki/
        # /wiki/aaa:bbb:
        # valid : /wiki/apple_pie
        # valie : /wiki/fruit/apple (not likely to occur)

        links = []
        for link_tag in all_link_tags:
            if 'href' in link_tag.attrs and link_tag.get_text() != 'ISBN':
                links.append((link_tag.get_text().lower(),
                              link_tag.get('href')))
        if settings.debug:
            debug_log('number of links: {}'.format(len(links)))
        return links

    def get_node_name(self):
        '''get the node name for the as the start name.
        O(n) where n is the approximately the size of HTML tree.
        '''
        try:
            title_node = self._soup.find(id="firstHeading")
            title = title_node.get_text().strip()
            if not title:
                raise ValueError('Cannot find title')

        except ValueError as e:
            log('Wikipedia change their DOM!')
            if settings.debug:
                debug_log(e)
            return None
        except Exception as e:
            log('iternal error detected')
            if settings.debug:
                debug_log(e)
            return None
        else:
            return title


def _test():
    '''some test to make sure it works
    '''
    test_cases = ['Mug', 'Star', 'Elephant', 'Cat', 'iphone', 'samsung']
    test_cases = ['Mug']
    for start in test_cases:
        test_crawler = Crawler(start)
        test_crawler.get_all_links()
        name = test_crawler.get_node_name()
        print(name)


if __name__ == '__main__':
    _test()
