'''
Searcher class
'''
import threading
from queue import Queue
from crawler import Crawler
from log import log, debug_log

debug = True

class Searcher(object):
    '''
    Searcher class
    '''
    def __init__(self, start, end):
        '''
        #TODO
        '''
        self.start = start.lower()
        self.end = end.lower()

        # stores all of the names
        self.todo_queue = Queue()

        self.reached = dict()
        self.path = None

        self.found_target = False

    # class variable
    _NUM_WORKER_THREADS = 20
    _FINISH_SIGNAL = '###DONE###'

    def run_search(self):
        '''
        perform BFS on the `Wiki graph`
        '''
        # {
        def worker():
            '''
            worker
            '''
            while not self.found_target:
            # {
                # get a task
                curr_vertex_name = self.todo_queue.get()
                if debug:
                    debug_log('##################now at ({})##############'\
                                .format(curr_vertex_name))

                # do work
                crawler = Crawler(curr_vertex_name)
                if not crawler.has_soup():
                    continue
                neighbours = crawler.get_all_link_names()
                # put all neighbours into todo_queue except ones already visited
                for neighbour_name in neighbours:
                    if neighbour_name not in self.reached and neighbour_name:
                        if neighbour_name in self.end or self.end in neighbour_name:
                            log('found target {}({})!'.format(self.end, neighbour_name))
                            if debug:
                                debug_log('change self.end from {} to {}'.format(
                                    self.end, neighbour_name))
                            self.end = neighbour_name
                            self.found_target = True
                            self.reached[neighbour_name] = curr_vertex_name
                            break
                        neighbour_name = neighbour_name.lower()
                        self.reached[neighbour_name] = curr_vertex_name
                        self.todo_queue.put(neighbour_name)
                # finish current task
                self.todo_queue.task_done()
            # } end while loop
            if debug:
                debug_log('killing threading...')
            self.todo_queue.task_done()
        # } end of worker()

        # apply BFS with the help of thread
        self.todo_queue.put(self.start)

        threads = []
        for _ in range(self._NUM_WORKER_THREADS):
            thr = threading.Thread(target=worker)
            thr.deamon = True
            threads.append(thr)
            thr.start()

        # block until all workers are done
        for thr in threads:
            debug_log('join thread...')
            thr.join()
        # self.todo_queue.join()

        try:
            if self.reached[self.end]:
                self.generate_path()
        except KeyError:
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
        path.append(self.start)
        self.path = path[::-1]


    def get_result(self):
        '''
        return a dict object containing all information
        '''
        res = dict()
        res['path'] = self.path
        try:
            res['degree'] = len(self.path) - 1
        except TypeError:
            res['degree'] = 0
        return res
