'''
Searcher class
'''
from queue import Queue
from crawler import Crawler
from log import log, debug_log


class Searcher(object):
    '''
    Searcher class
    '''
    def __init__(self, start, end):
        '''
        #TODO
        '''
        self.start = start
        self.end = end

        # stores all of the names
        self.todo_queue = Queue()
        self.reached = dict()
        self.path = None


    def run_search(self):
        '''
        perform BFS on the `Wiki graph`
        '''
        self.todo_queue.put(self.start)
        while not self.todo_queue.empty():
            curr_vertex_name = self.todo_queue.get()
            # get all of its neighbours
            crawler = Crawler(curr_vertex_name)

            if not crawler.has_soup():
                continue
            neighbours = crawler.get_all_link_names()
            # put all neighbours into todo_queue except ones already visited
            for neighbour_name in neighbours:
                if neighbour_name not in self.reached and neighbour_name:
                    self.reached[neighbour_name] = curr_vertex_name
                    self.todo_queue.put(neighbour_name)

        if self.reached.get(self.end):
            self.generate_path()
        else:
            log('Cannot reach {}'.format(self.end))


    def generate_path(self):
        '''
        trace back to generate path
        '''
        curr_vertex = self.end
        path = []
        while curr_vertex != self.start:
            path.append(curr_vertex)
            curr_vertex = self.reached[curr_vertex]
        self.path = path[::-1]


    def get_result(self):
        '''
        return a dict object containing all information
        '''
        res = dict()
        res['path'] = self.path
        try:
            res['degree'] = len(self.path)
        except TypeError:
            res['degree'] = 0
        return res
