 # Global variable attached to project which we are tracing
from pprint import pprint
DEBUG = 1

def dbg(*args):
    if DEBUG == 1:
        pprint(*args)
