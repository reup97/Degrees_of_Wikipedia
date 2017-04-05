'''
The main entry of degrees of wikipedia.
'''

from log import log
from searcher import Searcher
from send_email import send_email

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

def send_result():
    '''
    Send result to user's email since some searching
    takes really long time
    '''
    with open('logininfo.txt', 'r') as login:
        USER, PASSWORD = login.read().split()
    SUBJECT = 'results of degrees of wikipedia'
    BODY = ''
    with open('path_dict_result.txt', 'r') as result:
        for line in result:
            # eliminate lines with invalid ascii code
            BODY += line.encode('ascii', 'ignore').decode('ascii')

    try:
        send_email(USER, PASSWORD, USER, SUBJECT, BODY)
    except Exception as e:
        log('failed to send result')
        log(e)
        
    
def main():
    '''
    main entry of the program
    '''
    args = _init()

    if args.do_doctest:
        _test()
        return
    is_send_email = input('Do you want to send the results'
                          'to your email?[Y/n]')
    is_send_email = True if is_send_email in {'Y', 'y'} else False

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
        if is_send_email:
            send_result(USER, PASSWORD)        
        keystroke = input('press any key to continue, q to quick: ')
        if keystroke == 'q':
            break

if __name__ == '__main__':
    main()