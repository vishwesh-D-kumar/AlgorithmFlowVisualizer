import importlib
import sys
import inspect
from pathlib import Path
import astor
import ast
from pprint import pprint
from staticfg.builder import invert
import copy
import os
import graphviz as gv
from pprint import pprint
from pathlib import Path
import abc
# from memory_profiler import profile
DISALLOWED_FUNC_NAMES = {"<genexpr>", "<listcomp>", "<dictcomp>", "<setcomp>"}
STDLIB_DIR = Path(abc.__file__).parent
# Making a Nodevisitor to save calls
def merge_conditionals(prev, new):
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
        self.filepath = filepath
        with open(filepath, 'r') as src_file:
            src = src_file.read()
            tree = ast.parse(src)
            self.visit(tree)

    def visit_Call(self, node):
        self.lines_func_map[node.lineno] = node
        # self.lines_func_map[node.lineno] = self.lines_func_map.get(node.lineno, []) + [[node.func, node.args]]
        self.generic_visit(node)

    def generic_visit(self, node):
        if getattr(node, 'lineno', None):
            if self.curr_test is None:
                self.lines_conditional_map[node.lineno] = "No Test"
            else:
                self.lines_conditional_map[node.lineno] = astor.to_source(self.curr_test)
        super().generic_visit(node)

    def visit_If(self, node):
        # Storing last visited If, to see return condition
        # Saving current conditional,to put back later
        prev_test = self.curr_test
        self.curr_test = merge_conditionals(prev_test, node.test)
        # for child in node.body:
        #     self.visit(child)
        self.generic_visit(node)
        if node.orelse:
            self.curr_test = merge_conditionals(prev_test, invert(node.test))
            # self.generic_visit(node.orelse)
            for child in node.orelse:
                self.visit(child)
        self.curr_test = prev_test


class StackVisualizer:
    def __init__(self, filepath, func):
        self.stack = []
        self.prev_line = 0
        self.filepath = filepath
        self.calls_tracer_cache = {self.filepath: CallsVisitor(self.filepath)}
        self.calls_tracer = self.calls_tracer_cache[self.filepath]
        self.func = func
        self.output_dir = self.create_output_dir()
        print(self.output_dir,'$$$',self.filepath)
        self.graph = None
        self.prev_event = "line" #Avoiding tracing first function call, trivial
        self.prev_file = filepath
        self.step = 1
        self.final_dict = {}
        self.stdlib_cache = {}
        pprint(self.calls_tracer.lines_func_map)
        pprint(self.calls_tracer.lines_conditional_map)

    def is_stdlib(self, path):
        """
        helper function Taken from ccextractor/vardbg.
        checks if function stdlib
        """
        if path in self.stdlib_cache:
            return self.stdlib_cache[path]
        else:
            # Compare parents with known stdlib path
            status = STDLIB_DIR in Path(path).parents
            self.stdlib_cache[path] = status
            return status
    def trace_callback(self, frame, event, arg):
        # print("#########")
        # pprint(self.stack)
        # print("##########")
        # if self.prev_event == "call" or self.prev_event == "return":
        #     self.render()
            # input("Enter To continue")
        # print('###')
        # print(frame)
        # print(event)
        # print("###")
        # input()
        # print(lines_to_leave)
        if event == "call" and self.prev_line != 0:
            if frame.f_code.co_name in DISALLOWED_FUNC_NAMES:
                return
            if self.is_stdlib(frame.f_code.co_filename):
                return
            if self.prev_file not in self.calls_tracer_cache:
                self.calls_tracer_cache[self.prev_file] = CallsVisitor(self.prev_file)
            self.calls_tracer = self.calls_tracer_cache[self.prev_file]
            args_passed, _, _, locals = inspect.getargvalues(frame)
            call_made = astor.to_source(self.calls_tracer.lines_func_map[self.prev_line])
            if 'self' in args_passed: args_passed.remove('self')
            arg_values = {arg: copy.deepcopy(locals[arg]) for arg in args_passed}
            # print("YES")
            # print(args)
            # adding parameters
            # args_called.append(frame.f_locals)
            # addingframe for later testing
            # rebuild function
            # self.stack.append([frame, [astor.to_source(arg) for arg in c.lines_func_map[prev_line][0][1]]])
            self.stack.append([call_made, arg_values, self.prev_line])

            # self.stack.append([])

        if event == "return":
            if self.stack:
                return_condition = self.calls_tracer.lines_conditional_map[frame.f_lineno]
                self.render(arg, return_condition)
                print(self.stack.pop(), "popped with return", arg)
                print("return condition used ", return_condition)
        curr_file = frame.f_code.co_filename.replace('\\', '/')
        curr_file = os.path.abspath(curr_file)
        if event == "call":
            self.render()
        self.prev_line = frame.f_lineno
        self.prev_file = curr_file
        self.prev_event = event
        return self.trace_callback

    def generate_flow(self,*args,**kwargs):
        # global prev_line
        mod_name = Path(self.filepath).stem
        spec = importlib.util.spec_from_file_location(mod_name, self.filepath)
        mod = importlib.util.module_from_spec(spec)
        file_dir = os.path.dirname(self.filepath)
        sys.path.append(file_dir)
        spec.loader.exec_module(mod)
        func = getattr(mod, self.func, None)
        sys.settrace(self.trace_callback)
        func(*args,**kwargs)
        sys.settrace(None)

    def create_output_dir(self):
        """
        Creates a output directory
        :return output directory path
        """
        output_dir = os.path.dirname(self.filepath)
        try:
            os.mkdir(f'./{output_dir}/stack')

        except:
            pass
        return os.path.abspath(f'{output_dir}/stack')

    # @profile
    def render(self,ret_val=None,ret_condition=None):
        # TODO: Fix pdf output size
        # For vertical orientation use rankdir, {} for flipping orientation
        graph = gv.Digraph('Call Stack', filename='call_stack', node_attr={'shape': 'record'},format='png')
        # graph.graph_attr = {'size': '8.3,11.7!', 'ratio': 'fill','margin':'0'}
        call_stack = "{"
        i = 0
        for call in self.stack:
            called_as, args, line_no = call
            call_stack += "{"
            call_stack += f'<f{i}> {called_as.strip()}'
            call_stack += '| ' + 'line:' + str(line_no)
            formatted_args = str(args).strip()
            formatted_args=formatted_args.replace('{','\{')
            formatted_args=formatted_args.replace('}','\}')
            formatted_args=formatted_args.replace('[','\[')
            formatted_args=formatted_args.replace(']','\]')
            print(formatted_args,"###")
            call_stack +=  '| ' + 'args ' + formatted_args
            call_stack += "}|"
            i += 1
        call_stack = call_stack[:-1]
        call_stack += "}"
        if ret_condition is not None:
            graph.node('return_node', f'Condition used : {ret_condition}\n Return Value : {ret_val}',
                       _attributes={'shape': 'ellipse','color':'red'})
            graph.edge(f"call_stack:f{i - 1}", 'return_node',_attributes={'color':'red'})
        print(call_stack)
        graph.node('call_stack', call_stack)
        print("rendered at",f'{self.output_dir}/call_stack{self.step}')
        graph.render(filename=f'{self.output_dir}/call_stack{self.step}',view=False)
        self.final_dict[self.step]= {'line':self.prev_line,'images':f'call_stack{self.step}','return':True if ret_condition is not None else False}
        self.step += 1


# c = CallsVisitor("recursiontest.py")
# c = CallsVisitor("dptests.py")
# pprint(c.lines_conditional_map)
# flow = []
# stack = []
# args_called = []
# prev_line = 0


# def trace_callback(frame, event, arg):
#     print("#########")
#     pprint(self.stack)
#     print("##########")
#     # print('###')
#     # print(frame)
#     # print(event)
#     # print("###")
#     global prev_line
#     # input()
#     # print(lines_to_leave)
#     if event == "call" and prev_line != 0:
#         args_passed, _, _, locals = inspect.getargvalues(frame)
#         call_made = astor.to_source(c.lines_func_map[prev_line])
#         if 'self' in args_passed: args_passed.remove('self')
#         arg_values = {arg: copy.deepcopy(locals[arg]) for arg in args_passed}
#         # print("YES")
#         # print(args)
#         # adding parameters
#         # args_called.append(frame.f_locals)
#         # addingframe for later testing
#         # rebuild function
#         # self.stack.append([frame, [astor.to_source(arg) for arg in c.lines_func_map[prev_line][0][1]]])
#         self.stack.append([call_made, arg_values, frame.f_lineno])
#
#         self.stack.append([])
#     if event == "return":
#         if self.stack:
#             return_condition = c.lines_conditional_map[frame.f_lineno]
#             print(self.stack.pop(), "popped with return", arg)
#             print("return condition used ", return_condition)
#     prev_line = frame.f_lineno
#     return trace_callback

# @profile
def go(*args,**kwargs):
    filepath = kwargs.pop('file')
    func = kwargs.pop('func')
    # folder = '/Users/vishweshdkumar/Desktop/gsoc/finalwork/finalrepo/flowchart_gen/recursion_visualize/'
    # filepath = "recursiontest.py"
    # filepath = "dptests.py"
    jsonout = 'f.json'
    defaultfunc = "main"
    filepath = os.path.abspath(filepath)
    # print(generate_flow(filepath, defaultfunc))
    # print(flow)
    s = StackVisualizer(filepath, func)
    s.generate_flow(*args,**kwargs)
    return s

if __name__ == "__main__":
    go()
