'''
CommonAncestorsSearcher class
TODO: send data back to main
'''
import threading
from queue import Queue

import fileio
from crawler import Crawler
from log import log, debug_log
from settings import * # debug

LOCK = threading.Lock()

class CommonAncestorsSearcher(object):
    '''CommonAncestorsSearcher class
    '''
    def __init__(self, start1, start2, max_pages=1000):
        '''
        #TODO
        '''
        self._start = [start1.lower().strip(), start2.lower().strip()]
        self._max_page = max_pages
        # stores all the names
        self._todo_queues = [Queue(), Queue()]
        self._reached = [dict(), dict()]
        self._common_ancestors = set()

        self._path = None

        self.found_common_ancestor = False
        self._max_limit_reached = False

        # # load graphs cached in the graph_bank
        # # to search faster.
        # if debug:
        #     debug_log('loading all cached graphs...')
        # self._reached = fileio.read_all_graphs()

    # class variable
    _NUM_WORKER_THREADS = 20
    nodes_counter = 0

    def worker(self, num):
        '''worker which implements DFS on the graph of wikipedia.
        '''
        def common_ancestor_found():
            '''Check if common ancestors are found
            Return:
                a set of common ancestors if common ancesotrs are found;
                empty set otherwise.
            '''
            set1 = set(self._reached[0])
            set2 = set(self._reached[1])
            return set1 & set2


        while not self.found_common_ancestor and not self._max_limit_reached:
        # {
            # get a task
            curr_vertex_info = self._todo_queues[num].get()

            LOCK.acquire()
            try:
                self.nodes_counter += 1
            finally:
                LOCK.release()

            if self.nodes_counter > self._max_page:
                self._todo_queues[num].task_done()
                self._max_limit_reached = True
                log('Maximum page limit reached. Terminating...')
                return

            if debug:
                debug_log('##now at ({}), total {}, queue size {}##'
                          .format(curr_vertex_info,
                                  self.nodes_counter,
                                  self._todo_queues[num].qsize()))

            # check if the common ancestors are found
            common_ancestors = common_ancestor_found()
            if common_ancestors:
                self.found_common_ancestor = True
                self._common_ancestors = common_ancestors
                self._todo_queues[num].task_done()
                return

            # do work
            crawler = Crawler(start=curr_vertex_info[0],
                              relurl=curr_vertex_info[1])
            if not crawler.has_soup():
                # be tolerant, go to next iteration
                continue

            # get all link information; each element in neighbours
            # contains (name, url)
            neighbours = crawler.get_all_links()

            # put all neighbours into _todo_queue except ones already
            # visited
            for neighbour in neighbours:
                if (neighbour[0] not in self._reached[num]
                        and neighbour[0] not in curr_vertex_info[0]):
                    if self._reached[num][curr_vertex_info[0]] != neighbour[0]:
                        ######### ADD LOCK #######
                        LOCK.acquire()
                        try:
                            self._reached[num][neighbour[0]] = curr_vertex_info[0]
                        finally:
                            LOCK.release()
                    self._todo_queues[num].put(neighbour)
            # finish current task
            self._todo_queues[num].task_done()
        # } end while loop
        # Target has been found or max limit reached if goes here.
        if debug:
            debug_log('killing worker...')


    def run_search(self):
        '''Master: creates workers to do the graph search.
        '''
        # initialize bfs
        self._todo_queues[0].put((self._start[0], None))
        self._reached[0][self._start[0]] = self._start[0]

        self._todo_queues[1].put((self._start[1], None))
        self._reached[1][self._start[1]] = self._start[1]


        # apply BFS with the help of threads
        threads1 = []
        threads2 = []
        for _ in range(self._NUM_WORKER_THREADS//2):
            thr = threading.Thread(target=self.worker, args=(0,))
            # make sure the thread will eventually exit!
            thr.deamon = True
            threads1.append(thr)
            thr.start()

        for _ in range(self._NUM_WORKER_THREADS//2):
            thr = threading.Thread(target=self.worker, args=(1,))
            # make sure the thread will eventually exit!
            thr.deamon = True
            threads1.append(thr)
            thr.start()


        # block until all workers are done
        for thr in threads1+threads2:
            if debug:
                debug_log('join thread [{}]'.format(thr.name))
            thr.join()

        # program goes here iff graph search is done
        if self.found_common_ancestor:
            log('common ancestor(s) found: {}'.format(str(self._common_ancestors)))


    # def generate_path(self):
    #     '''Trace back to generate path
    #     Will raise a KeyError if a bad graph is parsed.
    #     '''
    #     curr_vertex = self._end
    #     path = []
    #     while curr_vertex != self._start:
    #         old_vertex = curr_vertex
    #         if debug:
    #             debug_log(curr_vertex)
    #         path.append(curr_vertex)
    #         curr_vertex = self._reached[old_vertex]
    #         # this is aimed to prevent from loop in the graph
    #         if curr_vertex == old_vertex:
    #             if debug:
    #                 debug_log('current vertex[{}] == old vertex[{}]'.
    #                           format(curr_vertex, old_vertex))
    #             break
    #     path.append(self._start)
    #     self._path = path[::-1]


    def get_result(self):
        '''return a dict object containing all information
        '''
        res = dict()
        res['path'] = self._path
        try:
            res['degree'] = len(self._path) - 1
        except TypeError:
            res['degree'] = 0
        # write the graph to a file
        if debug:
            debug_log('storing graph...')
        fileio.write_graph(self._reached)
        return res
