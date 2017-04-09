import os
import datetime
import subprocess
from log import debug_log

debug = True
BANK_PATH = 'graph_bank/'

def write_graph(graph):
    '''write the graph to a file.
    Argument:
        graph: a dictiction representation of a
               graph.
    Return:
        None
    '''
    lastest_file_name = 'path_dict_result.txt'

    # write results to a file.
    # lastest_file_name is the file that stores the lastest
    # result.
    with open(lastest_file_name, 'w') as result_file:
        if debug:
            debug_log('writing path dict to file')
        result_file.write(str(graph))

    # create a unique name for each file in the graph_bank
    basename = BANK_PATH + 'graph'
    suffix = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    filename = '_'.join([basename, suffix]) + '.txt'
    # copy the lastest result file to the graph_bank
    subprocess.run(['cp', lastest_file_name, filename])

def read_all_graphs():
    '''Read all graph files into a dictionary.
    Return:
        a dictionary containing all the dictionaries in the graph bank.
    '''
    ret_dict = {}

    for graph_file in os.listdir(BANK_PATH):
        if graph_file.startswith('graph'):
            graph_file_rel = BANK_PATH + graph_file
            tmp_dict = read_graph(graph_file_rel)
            ret_dict.update(tmp_dict)
    return ret_dict


def read_graph(graph_file):
    '''Read graph from a given file.
    Arguments:
        graph_file: a .txt file containing a stringified dictionary
                    representation of a graph.
    Return:
        a dictionary equivalent to the content of the given graph.
    '''
    with open(graph_file) as gf:
        # We assume that all graph_files are not polluted and
        # people are nice.
        return eval(gf.read())
