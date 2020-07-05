import importlib
import sys
import inspect
from pathlib import Path
import astor
import ast
from pprint import pprint
from staticfg.builder import invert


# Making a Nodevisitor to save calls
def merge_conditinals(prev, new):
    if not new:
        return prev
    if not prev:
        return new
    return ast.BoolOp(ast.And(), values=[prev, new])


class CallsVisitor(ast.NodeVisitor):
    def __init__(self, filepath):
        super().__init__()
        self.lines_func_map = {}
        self.lines_conditional_map = {}
        self.curr_test = None
        with open(filepath, 'r') as src_file:
            src = src_file.read()
            tree = ast.parse(src)
            self.visit(tree)

    def visit_Call(self, node):
        self.lines_func_map[node.lineno] = self.lines_func_map.get(node.lineno, []) + [[node.func, node.args]]
        self.generic_visit(node)

    def generic_visit(self, node):
        if getattr(node,'lineno',None):
            if self.curr_test is None:
                self.lines_conditional_map[node.lineno]=""
            else:
                self.lines_conditional_map[node.lineno] = astor.to_source(self.curr_test)
        super().generic_visit(node)

    def visit_If(self, node):
        # Storing last visited If, to see return condition
        # Saving current conditional,to put back later
        prev_test = self.curr_test
        self.curr_test = merge_conditinals(prev_test, node.test)
        # for child in node.body:
        #     self.visit(child)
        self.generic_visit(node)
        if node.orelse:
            self.curr_test = merge_conditinals(prev_test, invert(node.test))
            # self.generic_visit(node.orelse)
            for child in node.orelse:
                self.visit(child)
        self.curr_test = prev_test


c = CallsVisitor("recursiontest.py")
pprint(c.lines_conditional_map)
flow = []
stack = []
args_called = []
prev_line = 0


def trace_callback(frame, event, arg):
    # print('###')
    # print(frame)
    # print(event)
    # print("###")
    global prev_line
    # input()
    # print(lines_to_leave)
    if event == "call" and prev_line != 0:
        args, _, _, value_dict = inspect.getargvalues(frame)
        print("YES")
        print(args)
        # adding parameters
        args_called.append(frame.f_locals)
        # addingframe for later testing
        stack.append([frame, [astor.to_source(arg) for arg in c.lines_func_map[prev_line][0][1]]])
    if event == "return":
        if stack:
            print(stack.pop(), "popped with return", arg)
    prev_line = frame.f_lineno
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


if __name__ == "__main__":
    go()
