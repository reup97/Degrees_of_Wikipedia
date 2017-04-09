'''
A GUI wrapper class of degrees of wikipedia
Reference:
    The skeleton of this program is form this
    link[https://docs.python.org/3/library/tkinter.html#tkinter-life-preserver]
    with some changes.

'''
import tkinter as tk
from searcher import Searcher
from log import debug_log

debug = True


class WikiApp(tk.Frame):
    '''GUI version of degree of wikipedia
    '''
    _BACKGROUND_COLOR = 'white'
    def __init__(self, master=None):
        super().__init__(master)
        self.configure(background=self._BACKGROUND_COLOR)
        self.start_lemma_name = ''
        self.end_lemma_name = ''
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
        self.start_button = tk.Button(self,
                                      text='Start',
                                      command=self.start_search,
                                      bg=self._BACKGROUND_COLOR)
        self.result_text = tk.Text(self, width=40, height=10,
                                   bg=self._BACKGROUND_COLOR)
        # add widges to frame
        self.welcome_label.grid(columnspan=2)
        self.start_label.grid(row=1, column=0)
        self.start_entry.grid(row=1, column=1)
        self.end_label.grid(row=2, column=0)
        self.end_entry.grid(row=2, column=1)
        self.start_button.grid(columnspan=2)
        self.result_text.grid(columnspan=2)

    def display_text(self, content):
        '''Display `content` in Tk.Text widget.
        '''
        self.result_text.insert(tk.END, content)

    def clear_text(self):
        '''Clean up text area.
        '''
        self.result_text.delete(1.0, tk.END)

    def show_result(self, result):
        '''result: returned value from searcher.result()
                Ex: {'degree': 2,
                     'path': ['macbook', 'apple inc.',
                              'iphone 6s plus']}
        '''
        if debug:
            debug_log(result)
        self.clear_text()
        self.display_text('Got it!\n')
        self.display_text('Degree: ' + str(result['degree'])+ '\n')
        self.display_text('Path: ')
        res_path = result['path']
        for (i, node) in enumerate(res_path):
            self.display_text(node)
            if i != len(res_path) - 1:
                self.display_text(' --> ')


    def _help(self):
        '''Show the usages of the program.
        '''
        helptext = ('Welome to degrees of wikipedia!\n'
                    'There is a well-known idea called "six degrees of separation": '
                    'everything in this world can be connected by 6 steps or less '
                    'with others. This program simulates this thory in the world of '
                    'Wikipedia.\n'
                    'To find the relation between two words, enter them in the \'Start\' '
                    'and \'End\' entry.')
        self.display_text(helptext)

    def do_searching(self):
        '''Run search.
        '''
        # start searching
        self.display_text('Busy searching...')
        wiki_searcher = Searcher(self.start_lemma_name,
                                 self.end_lemma_name)
        wiki_searcher.run_search()
        # got it, display result
        self.show_result(wiki_searcher.get_result())

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

        # make sure both text entry has contents
        if not (self.start_lemma_name and self.end_lemma_name):
            self.display_text('Invalid input. Try again.')
            return
        self.do_searching()

def _init():
    '''initialize argparse.
    '''
    import argparse
    parser = argparse.ArgumentParser(
        description='Taxonomy service.',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-d", "-debug",
                        help="run in the debug mode",
                        action="store_true",
                        dest="debug")


    parser.add_argument("--doctest",
                        help="Run doctests instead.",
                        action="store_true",
                        dest="do_doctest")

    return parser.parse_args()

def _test():
    '''run doctest.
    '''
    print("Running doctests ...")
    import doctest
    doctest.testmod()
    print("... done.")

if __name__ == '__main__':
    args = _init()
    if args.do_doctest:
        _test()

    root = tk.Tk()
    root.title('Degrees Of WikiPedia')
    root.geometry('400x320')
    app = WikiApp(master=root)
    app.mainloop()
