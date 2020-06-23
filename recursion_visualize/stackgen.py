import importlib
import sys
import inspect
from pathlib import Path
import astor
import ast

#Making a variable watcher
#TODO : Add support for imports using dll library, by deepcopying globals
#TODO: remove tracing of stdlib functions
import sys
class VarWatcher(object):
    def __init__(self, frame,var, attr=None):
        self.changers=[]
        self.prev_frame = None
        self.var = var
        self.attr = attr
        self.val=self.get_val(frame)
        print("DONE")
        sys.settrace(self.trace)
    def get_val(self,frame):
        try:
            currvar=frame.f_locals[self.var]
            if  self.attr:
                return getattr(currvar, attr)
            return currvar
        except:
            return self.val
    def check_changed(self,frame):
        curr = self.get_val(frame)
        is_changed =  self.val!=curr
        self.val = curr
        self.changers.append(self.prev_frame)
        return is_changed

    def trace(self, frame, event, arg):
        print(frame)
        if event=='line':
            self.check_changed(frame)
        self.prev_frame=frame
        return self.trace


# Making a Nodevisitor to save calls
class CallsVisitor(ast.NodeVisitor):
    def __init__(self, filepath):
        super().__init__()
        self.lines_func_map = {}
        with open(filepath, 'r') as src_file:
            src = src_file.read()
            tree = ast.parse(src)
            self.visit(tree)

    def visit_Call(self, node):
        self.lines_func_map[node.lineno] = self.lines_func_map.get(node.lineno, []) + [[node.func, node.args]]
        self.generic_visit(node)



c = CallsVisitor("recursiontest.py")
c.lines_func_map

flow = []
stack = []
args_called = []
prev_line=0

def trace_callback(frame, event, arg):
    # print('###')
    # print(frame)
    # print(event)
    # print("###")
    global prev_line
    # input()
    # print(lines_to_leave)
    if event == "call" and prev_line!=0:
        args, _, _, value_dict = inspect.getargvalues(frame)
        print("YES")
        print(args)
        # adding parameters
        args_called.append(frame.f_locals)
        # addingframe for later testing
        stack.append([frame,[astor.to_source(arg) for arg in c.lines_func_map[prev_line][0][1]]])
    if event=="return":
        if stack:
            print(stack.pop(),"popped with return",arg)
    prev_line=frame.f_lineno
    return trace_callback


def generate_flow(file, function):
    global stack
    # global prev_line
    mod_name = Path(file).stem
    spec = importlib.util.spec_from_file_location(mod_name, file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    func = getattr(mod, function, None)
    sys.settrace(trace_callback)
    func()
    sys.settrace(None)
    return flow


def go():
    filepath = "recursiontest.py"
    jsonout = 'f.json'
    defaultfunc = "main"
    print(generate_flow(filepath, defaultfunc))
    print(flow)
    # i=0
    # w = VarWatcher(sys._getframe(0),'i')
    # # sys.settrace(w.trace)
    # i+=1
    #
    # i**=2
    # print("YES")
    # i//=2
    # # sys.settrace(None)
    # print(w.changers)
    # # sys.settrace(None)



if __name__ == "__main__":
    go()
