import importlib
import sys
import inspect
from pathlib import Path

flow = []
stack = []
args_called = []

def trace_callback(frame, event, arg):

    print('###')
    print(frame)
    print(event)
    print("###")
    # input()
    # print(lines_to_leave)
    if event=="call":
        args, _, _, value_dict = inspect.getargvalues(frame)
        print("YES")
        print(args)
        #adding parameters
        args_called.append(frame.f_locals)
        #addingframe for later testing
        stack.append([frame,event,arg])
    return trace_callback


def generate_flow(file, function):
    global stack
    mod_name = Path(file).stem
    spec = importlib.util.spec_from_file_location(mod_name, file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Get the function here regardless of which path we took above
    func = getattr(mod, function, None)
    sys.settrace(trace_callback)
    func()
    sys.settrace(None)
    return flow
def go():
    filepath = "recursiontest.py"
    jsonout = 'f.json'
    defaultfunc = "main"
    print(generate_flow(filepath,defaultfunc))
    print(flow)
if __name__=="__main__":
    go()