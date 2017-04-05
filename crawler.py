'''
a crawler used for parsing pages in wikipedia
'''
import re
import http
from urllib.error import URLError
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from log import debug_log, log

debug = True

class Crawler(object):
    '''
    crawler class
    '''
    def __init__(self, start=None, relurl=None):
        '''
        start: name of lemma at the starting point
        url: RELATIVE url
        '''
        self._start = start
        self._url = self._BASE_RUL + relurl if relurl is not None else None
        if debug:
            debug_log(self._url)

        self._soup = self._make_soup()


    # class varialbes
    _BASE_RUL = 'https://en.wikipedia.org'
    _HEADERS = {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

    def has_soup(self):
        '''check if the crawler has a non-empty soup'''
        return self._soup is not None

    def generate_full_url(self):
        url = self._BASE_RUL + '/wiki/' + self._start
        # get rid of non-ascii characters by encode + decode
        url = url.encode('ascii', 'ignore').decode('ascii')
        return url

    def _make_soup(self):
        '''
        send request, handle response, and get soup object
        '''

        try:
            # short circuit if crawler is initialized with url
            if self._url is None:
                self._url = self.generate_full_url()
                if debug:
                    debug_log('get request...')
                    debug_log('url is {}'.format(self._url))

            req = Request(self._url, headers=self._HEADERS)
            response = urlopen(req)
            soup = BeautifulSoup(response, "html5lib")

        except URLError as e:
            err_msg = 'Cannot open the page with name {}: {}'.format(
                    self._start, e)
            if debug:
                debug_log(err_msg)
            log(err_msg)
            return None

        except UnicodeDecodeError as e:
            # example: https://en.wikipedia.org/wiki/Kronkåsa
            # 'Kronkåsa' contains non-ascii characters
            err_msg = 'Cannot open the page with name {}: {}'.format(
                    self._start, e)
            if debug:
                debug_log(err_msg)
            log(err_msg)
            return None

        except http.client.BadStatusLine as e:
            err_msg = 'Cannot open the page with name {}: {}'.format(
                    self._start, e)
            if debug:
                debug_log(err_msg)
            log(err_msg)
            return None

        else:
            return soup


    def get_all_links(self):
        '''get all the links in one page, aka get all edges of one node
        Return: a list of tuples that the first element is the name and
        the second element its the RELATIVE url.
        '''

        # def filt_cond(link_tag):
        #     '''
        #     conditions for filtering good links
        #     '''
        #     cond = link_tag['href'].startswith('/wiki/')\
        #             and not link_tag['href'].startswith('/wiki/Category:')\
        #             and not link_tag['href'].startswith('/wiki/File:')\
        #             and not link_tag['href'].startswith('/wiki/Help:')\
        #             and not link_tag['href'].startswith('/wiki/International_Standard_Book_Number')\
        #             and not link_tag['href'].startswith('/wiki/Special:')\
        #             and not link_tag['href'].startswith('/wiki/Wikipedia:')
        #     return cond

        assert self.has_soup(), 'self._soup is None'

        all_link_tags = self._soup.find(id='bodyContent')\
                            .find_all('a', href=re.compile("^(/wiki/)((?!:).)*$"))

        # links = [link_tag.get_text() for link_tag in all_link_tags
        #          if filt_cond(link_tag)]
        links = [(link_tag.get_text().lower(), link_tag.get('href')) for link_tag in all_link_tags\
                 if 'href' in link_tag.attrs and link_tag.get_text() != 'ISBN']
        if debug:
            debug_log('number of links: {}'.format(len(links)))
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
        except Exception as e:
            log('iternal error detected')
            if debug:
                debug_log(e)
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
        test_crawler.get_all_links()
        name = test_crawler.get_node_name()
        print(name)


if __name__ == '__main__':
    _test()
