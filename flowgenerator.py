import importlib
import sys
from pathlib import Path

flow = []
lines_to_leave = set()

def trace_callback(frame,event,arg):
    # print('###')
    # print(frame)
    # print(event)
    # print("###")
    print(lines_to_leave)
    if not frame.f_lineno in lines_to_leave:
        flow.append(frame.f_lineno)
    return trace_callback


def generate_flow(file,function,leave):
    global lines_to_leave
    lines_to_leave=leave
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

# filepath = "test.py"
# jsonout = 'f.json'
# defaultfunc = "main"
# print(generate_flow(filepath,defaultfunc))
# print(flow)
