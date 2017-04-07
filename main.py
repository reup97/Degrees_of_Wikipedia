'''
The main entry of degrees of wikipedia.
'''

from searcher import Searcher


def _init():
    '''
    initialize argparse
    '''
    import argparse
    parser = argparse.ArgumentParser(
        description='Taxonomy service.',
        formatter_class=argparse.RawTextHelpFormatter,)

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

def _help():
    '''
    Show the usages of the program
    '''
    print('Welcome to Degrees_of_Wikipedia!')
    # TODO: enrich help doc later

def show_result(result):
    '''
    result: returned value from searcher.result()
    '''
    # TODO: enrich result later
    print(result)

def main():
    '''
    main entry of the program
    '''
    args = _init()

    if args.do_doctest:
        _test()
        return
    while True:
        _help()
        start_lemma_name = input('Starts at: ').strip().lower()
        end_lemma_name = input('Ends at: ').strip().lower()

        # start searching
        wiki_searcher = Searcher(start_lemma_name, end_lemma_name)
        wiki_searcher.run_search()
        # get results
        show_result(wiki_searcher.get_result())
        # send result to my email
        keystroke = input('press any key to continue, q to quick: ')

        if keystroke == 'q':
            break

def test_main():
    '''
    main entry of the TEST_program: no prompt
    '''
    args = _init()

    if args.do_doctest:
        _test()
        return
    while True:
        _help()
        start_lemma_name = input().strip().lower()
        end_lemma_name = input().strip().lower()

        # start searching
        wiki_searcher = Searcher(start_lemma_name, end_lemma_name)
        wiki_searcher.run_search()
        # get results
        show_result(wiki_searcher.get_result())

        keystroke = input()
        if keystroke == 'q':
            break


if __name__ == '__main__':
    main()
