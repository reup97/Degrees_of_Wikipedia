'''
msg pipped to stderr
'''
import sys

def debug_log(msg):
    '''
    msg pipped to stderr
    '''
    print('[Debug]{}'.format(msg), file=sys.stderr, flush=True)


def log(msg):
    '''
    msg pipped to stdout
    '''
    print('[Log]{}'.format(msg), file=sys.stdout, flush=True)
