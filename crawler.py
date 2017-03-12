'''
a crawler used for parsing pages in wikipedia
'''

from urllib.error import URLError
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from log import debug_log, log

debug = True

class Crawler(object):
    '''
    crawler class
    '''
    def __init__(self, start):
        '''
        start: name of lemma at the starting point
        end: name of lemma at the ending point
        '''
        self._start = start
        self._soup = self._make_soup()



    # class varialbes
    BASE_URL = 'https://en.wikipedia.org/wiki/'
    HEADERS = {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

    def has_soup(self):
        return self._soup is not None

    def _make_soup(self):
        '''
        send request, handle response, and get soup object
        '''
        try:
            url = self.BASE_URL + self._start
            url = url.encode('ascii', 'ignore').decode('ascii')

            if debug:
                debug_log('get request...')
                debug_log('url is {}'.format(url))
            req = Request(url, headers=self.HEADERS)
            response = urlopen(req)

            soup = BeautifulSoup(response, "html5lib")
        except URLError as e:
            err_msg = 'Cannot open the page with name {}: {}'.format(self._start, e)
            if debug:
                debug_log(err_msg)
            log(err_msg)
            return None
        except UnicodeDecodeError as e:
            # example: https://en.wikipedia.org/wiki/Kronkåsa
            err_msg = 'Cannot open the page with name {}: {}'.format(self._start, e)
            if debug:
                debug_log(err_msg)
            log(err_msg)
            return None
        else:
            return soup


    def get_all_link_names(self):
        '''
        get all the links in one page, aka get all edges of one node

        '''

        def filt_cond(link_tag):
            '''
            conditions for filtering good links
            '''
            cond = link_tag['href'].startswith('/wiki/')\
                    and not link_tag['href'].startswith('/wiki/Category:')\
                    and not link_tag['href'].startswith('/wiki/File:')\
                    and not link_tag['href'].startswith('/wiki/Help:')\
                    and not link_tag['href'].startswith('/wiki/International_Standard_Book_Number')\
                    and not link_tag['href'].startswith('/wiki/Special:')
            return cond

        assert (self._soup is not None), 'self._soup is None'

        all_link_tags = self._soup.find(id='bodyContent').find_all('a')

        links = [link_tag.get_text() for link_tag in all_link_tags
                 if filt_cond(link_tag)]
        if debug:
            debug_log('all valid neighbours:')
            for link in links:
                debug_log(link)
        return links


    def get_node_name(self):
        '''
        get the node name for the start
        '''
        try:
            title_node = self._soup.find(id="firstHeading")
            title = title_node.get_text().strip()
            if not title:
                raise ValueError('Cannot find title')

        except ValueError as e:
            log('Wikipedia change their DOM!')
            if debug:
                debug_log(e)
            return None
        except:
            log('iternal error detected')
            return None
        else:
            return title


def _test():
    '''
    some test to make sure it works
    '''
    test_cases = ['Mug', 'Star', 'Elephant', 'Cat', 'iphone', 'samsung']
    test_cases = ['Mug']
    for start in test_cases:
        test_crawler = Crawler(start)
        test_crawler.get_all_link_names()
        name = test_crawler.get_node_name()
        print(name)


if __name__ == '__main__':
    _test()