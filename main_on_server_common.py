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
from log import log, debug_log
from searcher_common import CommonAncestorsSearcher as Searcher
from send_email import send_email


def _help():
    '''Show the usages of the program
    '''
    print('Welcome to Degrees_of_Wikipedia!')
    # TODO: enrich help doc later


def show_result(result):
    '''result: returned value from searcher.result()
    '''
    log('path1: ' + str(result['path'][0]))
    log('path2: ' + str(result['path'][1]))
    log('degree: ' + str(result['degree']))

    #################
    # draw  graph####
    #################
    log('Rendering graphs...')
    nx.draw(result['graph1'], node_size=50)
    if settings.debug:
        debug_log('call plt to save the graph1...')
    # save graph as .png
    img_suffix = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
    plt.savefig('graph_img/graph_common_img1_'+img_suffix+'.png')

    nx.draw(result['graph2'], node_size=50)
    if settings.debug:
        debug_log('call plt to save the graph2...')
    # save graph as .png
    plt.savefig('graph_img/graph_common_img2_'+img_suffix+'.png')

    # write the graph to a file
    if settings.debug:
        debug_log('storing graph...')
    tmp_graphs = (str(result['graph1'].nodes()) + '\n' +
                  str(result['graph1'].edges()) + '\n' +
                  str(result['graph2'].nodes()) + '\n' +
                  str(result['graph2'].edges()))
    fileio.write_graph(tmp_graphs)


def send_result():
    '''Send result to user's email since some searching
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
    '''main entry of the program
    '''
    is_send_email = input('Do you want to send the results'
                          'to your email?[Y/n]')
    is_send_email = True if is_send_email in {'Y', 'y'} else False

    while True:
        _help()
        start1_lemma_name = input('start1 at: ').strip().lower()
        start2_lemma_name = input('start2 at: ').strip().lower()
        max_pages_limit = input('Max page limit: ').strip()
        while not max_pages_limit.isdigit():
            log('max page limit needs to be a integer.')
            max_pages_limit = input('Max page limit: ').strip()
        max_pages_limit = int(max_pages_limit)

        # start searching
        wiki_searcher = Searcher(start1_lemma_name, start2_lemma_name,
                                 max_pages_limit)
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
