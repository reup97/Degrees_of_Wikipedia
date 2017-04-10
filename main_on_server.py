'''
The main entry of degrees of wikipedia.
'''
import datetime
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

import settings
import fileio
from searcher import Searcher
from log import log, debug_log
from send_email import send_email


def _help():
    '''
    Show the usages of the program
    '''
    print('Welcome to Degrees_of_Wikipedia!')

def show_result(result):
    '''
    result: returned value from searcher.result()
    '''
    log('path: ' + str(result['path']))
    log('degree: ' + str(result['degree']))
    #################
    ## draw  graph###
    #################
    log('Rendering graph...')
    nx.draw_spectral(result['graph'], node_size=50)
    if settings.debug:
        debug_log('call plt to show the graph...')
    # save graph as .png
    img_suffix = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
    plt.savefig('graph_img/graph_img'+img_suffix+'.png')

    # write the graph to a file
    if settings.debug:
        debug_log('storing graph...')
    fileio.write_graph(str(result['graph'].nodes()) +
                       '\n' + str(result['graph'].edges()))


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
            send_result()
        keystroke = input('press any key to continue, q to quick: ')
        if keystroke == 'q':
            break

if __name__ == '__main__':
    main()
