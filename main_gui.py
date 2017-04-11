'''
A GUI wrapper class of degrees of wikipedia
Reference:
    The skeleton of this program is form this
    link[https://docs.python.org/3/library/tkinter.html#tkinter-life-preserver]
    with some changes.

'''
import datetime
import subprocess
import tkinter as tk
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import write_dot
from searcher import Searcher
from searcher_common import CommonAncestorsSearcher
from log import debug_log, log
import settings
import fileio


class WikiApp(tk.Frame):
    '''GUI version of degree of wikipedia
    '''
    _BACKGROUND_COLOR = 'white'

    def __init__(self, master=None):
        super().__init__(master)
        self.configure(background=self._BACKGROUND_COLOR)
        self.start_lemma_name = ''
        self.end_lemma_name = ''
        self.max_page_limit = 0
        self.pack()
        self.create_widges()
        self._help()

    def create_widges(self):
        '''create widges.
        '''
        self.welcome_label = tk.Label(self,
                                      text='Welcome to Degrees of Wikipedia!',
                                      bg=self._BACKGROUND_COLOR)
        self.start_label = tk.Label(self,
                                    text='Start at: ',
                                    bg=self._BACKGROUND_COLOR)
        self.end_label = tk.Label(self,
                                  text='End at: ',
                                  bg=self._BACKGROUND_COLOR)
        self.start_entry = tk.Entry(self)
        self.end_entry = tk.Entry(self)
        self.limit_label = tk.Label(self,
                                    text='Max. Page: ',
                                    bg=self._BACKGROUND_COLOR)
        self.limit_entry = tk.Entry(self)
        self.start_button = tk.Button(self,
                                      text='Start',
                                      command=self.start_search,
                                      bg=self._BACKGROUND_COLOR)
        self.exit_button = tk.Button(self,
                                     text="Exit",
                                     command=root.destroy,
                                     bg=self._BACKGROUND_COLOR)
        self.result_text = tk.Text(self, width=40, height=10,
                                   bg=self._BACKGROUND_COLOR)
        # add widges to frame
        self.welcome_label.grid(columnspan=4)
        self.start_label.grid(row=1, column=0)
        self.start_entry.grid(row=1, column=1, columnspan=3)
        self.end_label.grid(row=2, column=0)
        self.end_entry.grid(row=2, column=1, columnspan=3)
        self.limit_label.grid(row=3, column=0)
        self.limit_entry.grid(row=3, column=1, columnspan=3)
        self.start_button.grid(row=4, column=1)
        self.exit_button.grid(row=4, column=2, sticky=tk.W)
        self.result_text.grid(columnspan=2)

    def display_text(self, content):
        '''Display `content` in Tk.Text widget.
        '''
        self.result_text.insert(tk.END, content)

    def clear_text(self):
        '''Clean up text area.
        '''
        self.result_text.delete(1.0, tk.END)

    def render(self, nx_graph, path_list, figure=plt):
        '''Draw graph, store dot file, convert dot to pdf.
        '''
        #################
        # draw  graph####
        #################
        img_suffix = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
        img_name = 'graph_img/graph_img' + img_suffix
        dot_name = img_name + '.dot'
        if settings.debug:
            debug_log('generating {} file...'.format(dot_name))
        write_dot(nx_graph, dot_name)

        if settings.debug:
            debug_log('generating {}.pdf file from .dot'
                      'file...'.format(dot_name))
        # save graph as .png
        subprocess.run(['dot', '-Tpdf', '-O', dot_name])
        subprocess.run(['open', dot_name+'.pdf'])

        log('Rendering graph...')
        # nx.draw_spring(nx_graph, node_size=50)
        ###################################################
        # change color of node[ok] and path###
        ###################################################
        start_node = path_list[0]
        end_node = path_list[-1]
        nx_graph_pos = nx.spring_layout(nx_graph)
        nx.draw_networkx(nx_graph, nx_graph_pos,
                         with_labels=False,
                         node_size=50)
        # change color of nodes along the path
        nx.draw_networkx_nodes(nx_graph,
                               pos=nx_graph_pos,
                               nodelist=path_list,
                               node_color='g',
                               node_size=200)
        # change color of end-point nodes
        nx.draw_networkx_nodes(nx_graph,
                               pos=nx_graph_pos,
                               nodelist=[start_node, end_node],
                               node_color='b',
                               node_size=200)
        # change path color
        path_edge_list = [(path_list[i], path_list[i+1])
                          for i in range(len(path_list)-1)]
        nx.draw_networkx_edges(nx_graph,
                               pos=nx_graph_pos,
                               edgelist=path_edge_list,
                               width=1.0,
                               edge_color='b')

        # write the graph to a file
        if settings.debug:
            debug_log('storing graph...')
        fileio.write_graph(nx_graph.nodes())
        fileio.write_graph(nx_graph.edges())

        log('Done')
        plt.axis('off')
        figure.show()

    def show_result(self, result):
        '''show summary result, render graph, and store graph files.
           result: returned value from searcher.result()
                    Ex: {'degree': 2,
                            'path': ['macbook', 'apple inc.',
                                    'iphone 6s plus']
                            'graph':networkx.classes.digraph.Digraph
        '''
        log(result)
        self.clear_text()
        self.display_text('Got it!\n')
        self.display_text('Degree: ' + str(result['degree']) + '\n')
        self.display_text('Path: ')
        res_path = result['path']
        for (i, node) in enumerate(res_path):
            self.display_text(node)
            if i != len(res_path) - 1:
                self.display_text(' --> ')

        self.render(result['graph'], res_path)

    def _help(self):
        '''Show the usages of the program.
        '''
        helptext = ('Welome to degrees of wikipedia!\n'
                    'There is a well-known idea called "six degrees of '
                    'separation": everything in this world can be connected '
                    'by 6 steps or less with others. This program simulates '
                    'this thory in the world of Wikipedia.\n'
                    'To find the relation between two words, enter them in '
                    'the \'Start\'(\'Start1\') and \'End\'(\'Start2\') entry.')
        self.display_text(helptext)

    def do_searching(self):
        '''Run search.
        '''
        # start searching
        if not self.max_page_limit:
            wiki_searcher = Searcher(self.start_lemma_name,
                                     self.end_lemma_name)
        else:
            try:
                limit_int = int(self.max_page_limit)
            except ValueError:
                self.display_text('Invallid maximum limit.')
                return
            wiki_searcher = Searcher(self.start_lemma_name,
                                     self.end_lemma_name,
                                     limit_int)

        self.display_text('Busy searching...')
        log('Busy searching...')
        wiki_searcher.run_search()
        # got it, display result
        if wiki_searcher.found_target:
            self.show_result(wiki_searcher.get_result())
        else:
            self.clear_text()
            self.display_text('Search reach the maximum page limit.\n')
        # clean Entry for next search
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)

    def start_search(self):
        '''main entry of the program: get and check inputs.
        '''
        self.clear_text()
        # get input from Entry
        self.start_lemma_name = self.start_entry.get().strip()
        self.end_lemma_name = self.end_entry.get().strip()
        self.max_page_limit = self.limit_entry.get().strip()
        # make sure both text entry has contents
        if not (self.start_lemma_name and self.end_lemma_name):
            self.display_text('Invalid input. Try again.')
            return

        self.do_searching()


class WikiCommonAncestorsApp(WikiApp):
    '''GUI for finding common ancestors.
    '''

    def __init__(self, master=None):
        super().__init__(master)
        self.start1_lemma_name = ''
        self.start2_lemma_name = ''

    def create_widges(self):
        '''create widges.
        '''
        self.welcome_label = tk.Label(self,
                                      text=('Welcome to Degrees of Wikipedia, '
                                            'find common ancestors!'),
                                      bg=self._BACKGROUND_COLOR)
        self.start1_label = tk.Label(self,
                                     text='Start1 at: ',
                                     bg=self._BACKGROUND_COLOR)
        self.start2_label = tk.Label(self,
                                     text='Start2 at: ',
                                     bg=self._BACKGROUND_COLOR)
        self.start1_entry = tk.Entry(self)
        self.start2_entry = tk.Entry(self)
        self.limit_label = tk.Label(self,
                                    text='Max. Page: ',
                                    bg=self._BACKGROUND_COLOR)
        self.limit_entry = tk.Entry(self)
        self.start_button = tk.Button(self,
                                      text='Start',
                                      command=self.start_search,
                                      bg=self._BACKGROUND_COLOR)
        self.exit_button = tk.Button(self,
                                     text="Exit",
                                     command=root.destroy,
                                     bg=self._BACKGROUND_COLOR)
        self.result_text = tk.Text(self, width=40, height=10,
                                   bg=self._BACKGROUND_COLOR)
        # add widges to frame
        self.welcome_label.grid(columnspan=4)
        self.start1_label.grid(row=1, column=0)
        self.start1_entry.grid(row=1, column=1, columnspan=3)
        self.start2_label.grid(row=2, column=0)
        self.start2_entry.grid(row=2, column=1, columnspan=3)
        self.limit_label.grid(row=3, column=0, stick=tk.E)
        self.limit_entry.grid(row=3, column=1, columnspan=3)
        self.start_button.grid(row=4, column=1)
        self.exit_button.grid(row=4, column=2, sticky=tk.W)
        self.result_text.grid(columnspan=2)

    def show_result(self, result):
        '''show summary result, render graph, and store graph files.
           result: returned value from searcher.result()
                    Ex: {'degree': [2, 2]
                            'path': ['macbook', 'apple inc.',
                                    'iphone 6s plus']
                            'graph1':networkx.classes.digraph.Digraph
                            'graph2':networkx.classes.digraph.Digraph
                            ''
        '''
        log(result)
        self.clear_text()
        self.display_text('Got it!\n')
        self.display_text('Degree: ' + str(result['degree']) + '\n')
        self.display_text('Path: ')
        res_path1 = result['path'][0]
        res_path2 = result['path'][1]
        # show path in text format
        for (i, node) in enumerate(res_path1):
            self.display_text(node)
            if i != len(res_path1) - 1:
                self.display_text(' --> ')

        for (j, node) in enumerate(res_path2[::-1]):
            self.display_text(node)
            if j != len(res_path2) - 1:
                self.display_text(' <-- ')
        figure1 = plt.figure(0)
        self.render(result['graph1'], res_path1, figure=figure1)
        figure2 = plt.figure(1)
        self.render(result['graph2'], res_path2, figure=figure2)
        plt.show()

    def do_searching(self):
        '''Run search.
        '''
        # start searching
        if not self.max_page_limit:
            wiki_searcher = CommonAncestorsSearcher(self.start1_lemma_name,
                                                    self.start2_lemma_name)
        else:
            try:
                limit_int = int(self.max_page_limit)
            except ValueError:
                self.display_text('Invallid maximum limit.')
                return
            wiki_searcher = CommonAncestorsSearcher(self.start1_lemma_name,
                                                    self.start2_lemma_name,
                                                    limit_int)

        self.display_text('Busy searching...')
        log('Busy searching...')
        wiki_searcher.run_search()
        # got it, display result
        if wiki_searcher.found_common_ancestor:
            self.show_result(wiki_searcher.get_result())
        else:
            self.clear_text()
            if wiki_searcher.invalid_start_point:
                self.display_text('Invalid start point.')
            else:
                self.display_text('Search reach the maximum page limit.\n')

        # clean Entry for next search
        self.start1_entry.delete(0, tk.END)
        self.start2_entry.delete(0, tk.END)

    def start_search(self):
        '''main entry of the program: get and check inputs.
        '''
        self.clear_text()
        # get input from Entry
        self.start1_lemma_name = self.start1_entry.get().strip()
        self.start2_lemma_name = self.start2_entry.get().strip()
        self.max_page_limit = self.limit_entry.get().strip()
        if not (self.start1_lemma_name and self.start2_lemma_name):
            self.display_text('Invalid input. Try again.')
            return
        self.do_searching()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Degrees Of WikiPedia')
    root.geometry('800x640')
    root.configure(background='white')
    print('Welcome to degrees of wikiepedia!')
    which_app = input('1. Find path, 2. Find common ancestors: ').strip()
    while not which_app.isdigit() or not int(which_app) in (1, 2):
        log('invalid input. Please press 1 or 2.')
        which_app = input('1. Find path, 2. Find common ancestors')

    if which_app == '1':
        app = WikiApp(master=root)
    else:
        app = WikiCommonAncestorsApp(master=root)
    app.mainloop()
