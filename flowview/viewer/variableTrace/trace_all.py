from vardbg.debugger import Debugger


def debug_func(*args, **kwargs):
    dbg = Debugger(quiet=False)
    dbg.run(*args, **kwargs)
    return dbg

