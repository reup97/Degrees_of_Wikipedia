from crawler import Crawler
from searcher import Searcher
import tkinter as tk


def _init():
    '''
    initialize argparse
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
    '''
    run doctest
    '''
    print("Running doctests ...")
    import doctest
    doctest.testmod()
    print("... done.")

class WikiApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.start_entry = tk.Entry(self)
        self.end_entry = tk.Entry(self)
        self.start_button = tk.Button(self, text='Start',
                                      command=self.start_search)

        self.start_entry.grid(row=0)
        self.end_entry.grid(row=1)
        self.start_button.grid(columnspan=2)


    def _help(self):
        '''
        Show the usages of the program
        '''
        print('Welcome to Degrees_of_Wikipedia!')
        # TODO: enrich help doc later

    def show_result(self, result):
        '''
        result: returned value from searcher.result()
        '''
        # TODO: enrich result later
        print(result)
        self.result_label = tk.Label(self, text=''.format(str(result)))
        self.result_label.grid(rowspan=2)

    def start_search(self):
        '''
        main entry of the program
        '''
        self.start_lemma_name = self.start_entry.get()
        self.end_lemma_name = self.end_entry.get()
        # start searching
        wiki_searcher = Searcher(self.start_lemma_name, 
                                 self.end_lemma_name)
        wiki_searcher.run_search()
        # get results
        self.show_result(wiki_searcher.get_result())
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)

if __name__ == '__main__':
    args = _init()
    if args.do_doctest:
        _test()
    app = WikiApp()
    app.mainloop()

