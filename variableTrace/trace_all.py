from vardbg.debugger import Debugger


def debug_func(*args, **kwargs):
    dbg = Debugger()
    dbg.run(*args, **kwargs)
    return dbg
