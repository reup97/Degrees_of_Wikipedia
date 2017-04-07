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
        self._start = start.lower().strip()
        self._end = end.lower().strip()

        # stores all of the names
        self._todo_queue = Queue()

        self._reached = dict()
        self._path = None

        self.found_target = False

    # class variable
    _NUM_WORKER_THREADS = 20
    nodes_counter = 0

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
                curr_vertex_info = self._todo_queue.get()
                #
                self.nodes_counter += 1
                if debug:
                    debug_log('##now at ({}), total {}, queue size {}##'
                              .format(curr_vertex_info,
                                      self.nodes_counter,
                                      self._todo_queue.qsize()))
                if self._end in curr_vertex_info[0]:
                    log('$$found target {}({})!$$'.format(self._end,
                                                          curr_vertex_info))
                    # modify self._end:
                    self._end = curr_vertex_info[0]
                    self.found_target = True
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
                            self._reached[neighbour[0]] = curr_vertex_info[0]
                        self._todo_queue.put(neighbour)
                        if self._end in neighbour[0]:
                            log('$$found target {}({})!$$'.format(
                                self._end, neighbour[0]))
                            # modify self._end info
                            self._end = neighbour[0]
                            self.found_target = True
                            return
                # finish current task
                self._todo_queue.task_done()
            # } end while loop
            if debug:
                debug_log('killing worker...found target')
            self._todo_queue.task_done()
        # } end worker()

        # apply BFS with the help of thread
        # initialize bfs
        self._todo_queue.put((self._start, None))
        self._reached[self._start] = self._start

        threads = []
        for _ in range(self._NUM_WORKER_THREADS):
            thr = threading.Thread(target=worker)
            thr.deamon = True
            threads.append(thr)
            thr.start()

        # block until all workers are done
        for thr in threads:
            debug_log('join thread [{}]'.format(thr.name))
            thr.join()

        try:
            if self._reached[self._end]:
                self.generate_path()
        except KeyError:
            log('Cannot reach {} while generating path'.format(self._end))


    def generate_path(self):
        '''
        trace back to generate path
        '''
        curr_vertex = self._end
        path = []
        while curr_vertex != self._start:
            old_vertex = curr_vertex
            if debug:
                debug_log(curr_vertex)
            path.append(curr_vertex)
            curr_vertex = self._reached[old_vertex]
            # this is aimed to prevent from loop in the graph
            if curr_vertex == old_vertex:
                if debug:
                    debug_log('current vertex[{}] == old vertex[{}]'.
                              format(curr_vertex, old_vertex))
                break
        path.append(self._start)
        self._path = path[::-1]


    def get_result(self):
        '''
        return a dict object containing all information
        '''
        res = dict()
        res['path'] = self._path
        try:
            res['degree'] = len(self._path) - 1
        except TypeError:
            res['degree'] = 0
        # write results to file
        with open('path_dict_result.txt', 'w') as f:
            if debug:
                debug_log('writing path dict to file')
            f.write(str(res))
            f.write(str(self._reached))
        return res
