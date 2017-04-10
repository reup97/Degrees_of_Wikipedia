'''
Searcher class
'''
import threading
from queue import Queue
import networkx as nx


import fileio
from crawler import Crawler
from log import log, debug_log
import settings # debug

LOCK = threading.Lock()

class Searcher(object):
    '''Searcher class
    '''
    def __init__(self, start, end, max_pages=1000):
        '''
        #TODO
        '''
        self._start = start.lower().strip()
        self._end = end.lower().strip()
        self._max_page = max_pages
        # stores all the names
        self._todo_queue = Queue()

        self._reached = dict()
        self._path = None
        self._nx_digraph = nx.DiGraph()


        self.found_target = False
        self._max_limit_reached = False

        # # load graphs cached in the graph_bank
        # # to search faster.
        # if settings.debug:
        #     debug_log('loading all cached graphs...')
        # self._reached = fileio.read_all_graphs()

    # class variable
    _NUM_WORKER_THREADS = 20
    nodes_counter = 0

    def worker(self):
        '''worker which implements DFS on the graph of wikipedia.
        '''
        def target_found(tar):
            '''Notify user that the target is found and prepare
            for killing this worker.
            '''
            log('$$found target {}({})!$$'.format(self._end,
                                                  curr_vertex_info))
            # modify self._end:
            LOCK.acquire()
            try:
                self._end = tar
                self.found_target = True
                self._todo_queue.task_done()
            finally:
                LOCK.release()

        while not self.found_target and not self._max_limit_reached:
        # {
            # get a task
            curr_vertex_info = self._todo_queue.get()
            LOCK.acquire()
            try:
                self.nodes_counter += 1
            finally:
                LOCK.release()
            if self.nodes_counter > self._max_page:
                self._todo_queue.task_done()
                self._max_limit_reached = True
                log('Maximum page limit reached. Terminating...')
                return

            if settings.debug:
                debug_log('##now at ({}), total {}, queue size {}##'
                          .format(curr_vertex_info,
                                  self.nodes_counter,
                                  self._todo_queue.qsize()))
            if self._end in curr_vertex_info[0]:
                target_found(curr_vertex_info[0])
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
                if (neighbour[0] not in self._reached
                        and neighbour[0] not in curr_vertex_info[0]):
                    if self._reached[curr_vertex_info[0]] != neighbour[0]:
                        ######### ADD LOCK #######
                        LOCK.acquire()
                        try:
                            #################
                            ## update graph##
                            #################
                            self._nx_digraph.add_edge(curr_vertex_info[0], neighbour[0])
                            self._reached[neighbour[0]] = curr_vertex_info[0]
                        finally:
                            LOCK.release()
                    self._todo_queue.put(neighbour)
                    if self._end in neighbour[0]:
                        target_found(neighbour[0])
                        return
            # finish current task
            self._todo_queue.task_done()
        # } end while loop
        # Target has been found or max limit reached if the thread goes here.
        if settings.debug:
            debug_log('killing worker...')
        # self._todo_queue.task_done()


    def run_search(self):
        '''Master: creates workers to do the graph search.
        '''
        # initialize bfs
        self._todo_queue.put((self._start, None))
        self._reached[self._start] = self._start

        # apply BFS with the help of threads
        threads = []
        for _ in range(self._NUM_WORKER_THREADS):
            thr = threading.Thread(target=self.worker)
            # make sure the thread will eventually exit!
            thr.deamon = True
            threads.append(thr)
            thr.start()

        # block until all workers are done
        for thr in threads:
            if settings.debug:
                debug_log('join thread [{}]'.format(thr.name))
            thr.join()

        # program goes here iff graph search is done
        if self.found_target:
            try:
                if self._reached[self._end]:
                    self.generate_path()
            except KeyError:
                log('Cannot reach {} while generating path'.format(self._end))


    def generate_path(self):
        '''Trace back to generate path
        Will raise a KeyError if a bad graph is parsed.
        '''
        curr_vertex = self._end
        path = []
        while curr_vertex != self._start:
            old_vertex = curr_vertex
            if settings.debug:
                debug_log(curr_vertex)
            path.append(curr_vertex)
            curr_vertex = self._reached[old_vertex]
            # this is aimed to prevent from loop in the graph
            if curr_vertex == old_vertex:
                if settings.debug:
                    debug_log('current vertex[{}] == old vertex[{}]'.
                              format(curr_vertex, old_vertex))
                break
        path.append(self._start)
        self._path = path[::-1]


    def get_result(self):
        '''return a dict object containing all information
        '''
        res = dict()
        res['path'] = self._path
        try:
            res['degree'] = len(self._path) - 1
        except TypeError:
            res['degree'] = 0
        #####################
        ## add graph to res##
        #####################
        res['graph'] = self._nx_digraph
        # write the graph to a file
        if settings.debug:
            debug_log('storing graph...')
        fileio.write_graph(self._reached)
        return res
