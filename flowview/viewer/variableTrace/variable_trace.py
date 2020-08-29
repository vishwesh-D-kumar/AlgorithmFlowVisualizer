# import traceback
# TODO: remove tracing of stdlib functions
from pathlib import Path
import importlib.util
import sys
import os
import re
import inspect
import copy
import abc
from ..variableTrace.treevisualize import VisualTree, FullVisualTree
from pprint import pprint
module_type = type(sys)
# from treevisualize import VisualTree, FullVisualTree
ALLOWED_EVENTS = {"call", "line", "return"}
DISALLOWED_FUNC_NAMES = {"<genexpr>", "<listcomp>", "<dictcomp>", "<setcomp>"}

# Known stdlib module path
STDLIB_DIR = Path(abc.__file__).parent


class Variable:
    __slots__ = ['name', 'deepcopy_val', 'val', 'attr', 'history', 'prev', 'is_global', 'obj_val','is_module']

    def __init__(self, name, val, attr, obj):
        self.name = name
        self.deepcopy_val = copy.deepcopy(val)
        self.attr = attr
        self.val = val
        self.obj_val = obj
        self.history = []
        self.prev = None  # Pointer to the previous Variable, if any
        self.is_global = False
        self.is_module = (type(self.obj_val)==module_type)


    def check(self, frame, prev_line):

        if self.is_global:
            new, obj = get_variable_val(self, frame.f_globals)
        else:
            try:
                new, obj = get_variable_val(self, frame.f_locals)
            except KeyError:
                new, obj = get_variable_val(self, frame.f_globals)
                print("global used with", self.name)
                self.is_global = True
        old = self.deepcopy_val
        changed = False
        if new != old:
            print("Variable changed from", old, "to", new, "on line", prev_line)
            changed = True
        self.deepcopy_val = copy.deepcopy(new)
        self.val = new
        self.obj_val = obj
        if changed:
            str1 = self.name
            if self.attr:
                str1 += "." + self.attr
            curr_file = frame.f_code.co_filename.replace('\\', '/')
            curr_file = os.path.abspath(curr_file).lower()
            return str1,old, self.deepcopy_val, prev_line,curr_file

    def __repr__(self):
        return f"{self.name} ,{self.attr}, {self.val}"


def is_mutable(obj):
    immutable_types = [bool, int, float, tuple, str, frozenset]
    return type(obj) not in immutable_types


def process_change(new_val, old_val, var_name, line_no, changes):
    changes.append([copy.deepcopy(new_val), old_val, var_name, line_no])


def get_val(name, attr, f_locals):
    obj = f_locals[name]
    val = None
    if attr:
        val = getattr(obj, attr)
    else:
        val = obj
    return val, obj


def get_variable_val(var: Variable, f_locals):
    if var.is_module:
        return getattr(var.obj_val,var.attr),var.obj_val
    return get_val(var.name, var.attr, f_locals)


class Tracer:
    def __init__(self, file, func, include_files=[]):
        # Add a global tracer
        self.global_tracer = LocalsTracer(None, -1)
        self.local_tracers_stack = []  # Stack of local tracers , 1 per frame
        self.prev_line = 0
        self.include_files = [os.path.abspath(file).lower() for file in include_files]  # Files to include while tracing
        file = os.path.abspath(file)  # In case of relative naming
        file_dir = os.path.dirname(file)
        # IMP:Does not support case sensitive files right now
        self.changes = []
        self.file = file
        self.func = func
        self.final_dict = {}
        self.step = 1
        self.prev_file =file
        self.stdlib_cache = {}
        self.global_tracer_file = {file:self.global_tracer}
        self.module_vars = []

    def new_frame(self, frame):
        passed_locals = []
        new_tracer = LocalsTracer(frame, self.prev_line)
        if not self.local_tracers_stack:  # First Stack Frame
            self.local_tracers_stack.append(new_tracer)
            return
        old_tracer = self.local_tracers_stack[-1]
        variables_to_check = old_tracer.variables
        curr_file = os.path.abspath(frame.f_code.co_filename)
        if self.prev_file !=curr_file:
            variables_to_check+=self.global_tracer.variables
        for var in variables_to_check:
            if is_mutable(var.val) or is_mutable(var.obj_val):
                for name_new in frame.f_locals:
                    if frame.f_locals[name_new] is var.val or frame.f_locals[name_new] is var.obj_val:
                        if type(var) == Variable:
                            new_var = Variable(name_new, var.val, var.attr, var.obj_val)
                            new_var.history = var.history + [var.name]
                        if type(var) == VisualTree:
                            new_var = VisualTree(name=name_new, val=var.val, left=var.left, right=var.right,
                                                 obj=var.obj_val)
                            new_var.step_count = var.step_count
                        if type(var) == FullVisualTree:
                            new_var = FullVisualTree(name=name_new, val=var.val, child=var.child,
                                                     obj=var.obj_val)
                            new_var.step_count = var.step_count

                        new_tracer.add(new_var)
                        print(var, "->", new_var)
        print("Variables transferred are", new_tracer.variables)
        self.local_tracers_stack.append(new_tracer)
        # Transfer Locals that are transferred with calls (Mutable only)

    def set_global_tracer(self,file):
        file = os.path.abspath(file)
        if file not in self.global_tracer_file:
            self.global_tracer_file[file] = LocalsTracer(None, -1) 
        self.global_tracer= self.global_tracer_file[file]
            

    def trace(self, frame, event, arg):

        if not self.check_in_path(frame):
            return
        self.set_global_tracer(self.prev_file)
        # print(frame.f_lineno,frame.f_code.co_filename,self.include_files)
        self.final_dict[self.step] = {'line':self.prev_line,'changes':[],'images':[],'file':self.prev_file,'vars':[],'event':event}
        if event == "call":
            print("New trace initialized at", frame.f_lineno)
            self.new_frame(frame)
        curr_local_tracer = self.local_tracers_stack[-1]

        local_changes, globals_found = curr_local_tracer.trace(frame, event,
                                                               arg)  # changes processed from the local tracer

        for eve in local_changes:
            if type(eve) == str:
                self.final_dict[self.step]['images'].append(eve)
            else:
                self.final_dict[self.step]['changes'].append(eve)

        self.changes.extend(local_changes)

        for var, type_var in globals_found:
            print(type_var,var.name,"#$%")
            if var.is_module:
                if type_var:
                    s = type_var
                    type_var, referrer_name = s
                    for module_var in self.module_vars:
                        if referrer_name == module_var.name and type_var == type(module_var):
                            module_var.add_referrer(var)
                            break
                self.module_vars.append(var) # check if already there
                continue
            if type_var:
                s = type_var
                type_var, referrer_name = s
                for global_var in self.global_tracer.variables:
                    if referrer_name == global_var.name and type_var == type(global_var):
                        global_var.add_referrer(var)
                        break
            self.global_tracer.add(var)
            print(var, "global found")
        # print(self.global_tracer.toadd, "toadd", self.global_tracer)
        # print("Tracing globals")
        global_changes, globals_found = self.global_tracer.trace(frame, event, arg)  # Checking global changes
        # print("Done with global tracing")
        for eve in global_changes:
            if type(eve) == str:
                self.final_dict[self.step]['images'].append(eve)
            else:
                self.final_dict[self.step]['changes'].append(eve)

        self.changes.extend(global_changes)
        module_changes = []
        weights = {VisualTree:1,FullVisualTree:2}
        self.module_vars.sort(key = lambda x:weights.get(type(x),0))
        for var in self.module_vars:
            change = var.check(frame, self.prev_line)
            if change:
                module_changes.append(change)

        self.changes.extend(module_changes)
        for eve in module_changes:
            if type(eve) == str:
                self.final_dict[self.step]['images'].append(eve)
            else:
                self.final_dict[self.step]['changes'].append(eve)
        if event=="call":
            for var in self.global_tracer.variables+self.module_vars:
                if type(var)==VisualTree or type(var)==FullVisualTree:
                    continue
                variable_rep = var.name if var.attr is None else var.name+"."+var.attr
                self.final_dict[self.step]['vars'].append((variable_rep,var.deepcopy_val))

        else:
            for var in curr_local_tracer.variables+self.global_tracer.variables+self.module_vars:
                if type(var)==VisualTree or type(var)==FullVisualTree:
                    continue
                variable_rep = var.name if var.attr is None else var.name+"."+var.attr
                self.final_dict[self.step]['vars'].append((variable_rep,var.deepcopy_val))

        self.prev_line = frame.f_lineno
        self.prev_file = os.path.abspath(frame.f_code.co_filename)
        if event == "return":
            # Remove current tracer from stack
            self.local_tracers_stack.pop()
            # Return , as nothing else executed on this statement
            # return
        if local_changes or global_changes:
            self.render(local_changes + global_changes)
        self.step +=1
        return self.trace
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
    def check_in_path(self, frame):
        """
        Returns whether file in current included files
        If no included file given , return true for all
        :param frame:current frame to be checked
        :return: true if match or no files given to include , else false.
        """
        if frame.f_code.co_name in DISALLOWED_FUNC_NAMES:
            return False
        if self.is_stdlib(frame.f_code.co_filename):
            return False
        if self.include_files:
            curr_file = frame.f_code.co_filename.replace('\\', '/')
            curr_file = os.path.abspath(curr_file).lower()
            print(curr_file,self.include_files)
            return True in [curr_file.startswith(included_file.lower()) for included_file in self.include_files]
        return True

    def render(self, changes):
        for tracer in reversed(self.local_tracers_stack):
            print("----------------")
            print("|", tracer, "|")
            print("-----------------")
        print("Changes seen are", *changes)
        # input("Press Enter to continue")

    def run_func(self, *args, **kwargs):
        """runs function for tracing with given args"""

        mod_name = Path(self.file).stem
        spec = importlib.util.spec_from_file_location(mod_name, self.file)
        mod = importlib.util.module_from_spec(spec)
        file = os.path.abspath(self.file)  # In case of relative naming
        file_dir = os.path.dirname(file)
        sys.path.append(file_dir)
        spec.loader.exec_module(mod)
        func = getattr(mod, self.func, None)
        sys.settrace(self.trace)
        func(*args, **kwargs)
        sys.settrace(None)
        


class LocalsTracer:
    __slots__ = ['func', 'vals', 'names', 'attrs', 'variables', 'comments', 'lines_comments', 'toadd', 'prev_line',
                 'deepcopy_vals']

    def __init__(self, frame, prev_line):
        # Tuple storing location of function
        if frame is None:
            # GlobalTracer
            self.func = (0, "Global Frame")
        else:
            self.func = (frame.f_lineno, frame.f_code.co_name)
        self.vals = []  # Values attached by reference : used for is check while passing variables
        self.names = []
        self.attrs = []
        self.deepcopy_vals = []  # Values attached by reference : used to check for change in value
        self.comments = []
        self.lines_comments = {}
        self.toadd = []  # variables parsed from last line comments
        self.variables = []
        # self.val=self.getval(frame.f_locals)
        self.prev_line = prev_line
        # self.prev_event="line"

    # def add(self, name, val, attr=None, is_global=False):
    #     self.vals.append(val)
    #     self.deepcopy_vals.append(copy.deepcopy(val))
    #     self.names.append(name)
    #     self.attrs.append(attr)
    #     new_var = Variable(name, copy.deepcopy(val), attr)
    #     new_var.is_global = is_global
    #     self.variables.append(new_var)

    def add(self, var):
        cmp_name = var.name
        if type(var)!= VisualTree and type(var)!=FullVisualTree and var.attr :
            cmp_name+="."+var.attr
        for var_stored in self.variables:
            stored_name = var_stored.name
            if type(var_stored)!= VisualTree and type(var_stored)!=FullVisualTree and var_stored.attr:
                stored_name+="."+var_stored.attr
            if stored_name==cmp_name:
                return
        self.variables.append(var)

    def check(self, frame):
        f_locals = frame.f_locals
        changes = []
        # for idx in range(len(self.vals)):
        #     obj = self.names[idx]
        #     attr = self.attrs[idx]
        #     new = get_val(obj, attr, f_locals)
        #     if new != self.deepcopy_vals[idx]:
        #         print(self.names[idx], "changed on line ", self.prev_line, " from value ", self.vals[idx], "to value",
        #               new)
        #         process_change(new, self.deepcopy_vals[idx], self.names[idx], self.prev_line, changes)
        #     self.vals[idx] = new
        #     self.deepcopy_vals[idx] = copy.deepcopy(new)  # Deepcopying to avoid mutability errors
        weights = {VisualTree:1,FullVisualTree:2}
        self.variables.sort(key = lambda x:weights.get(type(x),0))
        for var in self.variables:
            change = var.check(frame, self.prev_line)
            if change:
                changes.append(change)
        return changes

    def get_comments(self, frame):
        if frame.f_lineno not in self.lines_comments:

            # Extracting source of entire current function
            lines, lineno = inspect.getsourcelines(frame)

            currline = lineno
            for line in lines:
                match = re.match(r"# watchvar (.+)$|^.+# watchvar (.+)$", line)
                comment = None
                if match:
                    comment = match.group(1) or match.group(2)  # Take whichever matches
                self.lines_comments[currline] = comment
                currline += 1
        return self.lines_comments[frame.f_lineno]

    def trace(self, frame, event, arg):
        # Adding variables defined on last line's  comments
        # print(self.toadd, frame.f_lineno, "TOADD")
        is_tracer_global = (0, "Global Frame") == self.func
        if is_tracer_global:
            try:
                changes = self.check(frame)
                self.prev_line = frame.f_lineno
                return changes, []
            except KeyError:  # Variable not a global in this file
                pass
            self.prev_line = frame.f_lineno
            return [], []
        changes = []
        globals_found = []
        while self.toadd:
            name, attr, var_type = self.toadd.pop()
            new_var = None
            is_global = False
            try:
                val, obj = get_val(name, attr, frame.f_locals)

            except KeyError:
                val, obj = get_val(name, attr, frame.f_globals)
                is_global = True

            if var_type:
                var_type = var_type.split(":")

                if var_type[0] == "btree":
                    left = var_type[1]
                    right = var_type[2]
                    val_attr = var_type[3]
                    new_var = VisualTree(name=name, obj=val, left=left, right=right, val=val_attr)
                if var_type[0] == "tree":
                    child = var_type[1]
                    val_attr = var_type[2]
                    new_var = FullVisualTree(name=name, obj=val, child=child, val=val_attr)
                if var_type[0] == "ref":
                    referrer_name = var_type[1]
                    print("Yes found a ref", referrer_name, name)

                    if var_type[2] == "btree":
                        treetype = VisualTree
                    if var_type[2] == "tree":
                        treetype = FullVisualTree

                    f = False
                    for var_local in self.variables:
                        print(var_local.name, referrer_name, type(var_local), treetype)
                        if var_local.name == referrer_name and type(var_local) == treetype:
                            new_var = Variable(name, val, attr, obj)
                            var_local.add_referrer(new_var)
                            print("attached referrer")
                            f = True
                            break
                    if not f:
                        globals_found.append((Variable(name, val, attr, obj), (treetype, referrer_name)))

            else:
                new_var = Variable(name, val, attr, obj)
                new_var.is_global = is_global
            if is_global:
                globals_found.append((new_var, None))
            else:
                if new_var is not None:
                    print("adding Variable", name, self)
                    self.add(new_var)

        changes = self.check(frame)
        if event == "line" or event == "return":
            # print(frame.f_locals)
            comment = self.get_comments(frame)
            if comment:
                comment = comment.strip()

                # Getting lines to be called added on next step
                # print(comment)
                parts = comment.split()
                # print(parts)
                parts = parts[-1].split('.')
                # print(parts)
                if len(parts) == 1:  # implies no attribute defined, a simple variable
                    part2 = comment.split()
                    if len(part2) > 1:
                        # print("YASSSSSS")
                        # print(parts)
                        # print(part2)
                        self.toadd.append((parts[0], None, part2[0]))

                    else:
                        self.toadd.append((parts[0], None, None))
                else:
                    # self.toadd.append((parts[0], parts[1]))
                    part2 = comment.split()
                    if len(part2) > 1:
                        self.toadd.append((parts[0], parts[1], part2[0]))

                    else:
                        self.toadd.append((parts[0], parts[1], None))
            self.prev_line = frame.f_lineno
        return changes, globals_found
        # self.prev_event=event
        # return self.trace

    def __str__(self):
        return str(self.func) + ' Frame'

    def __repr__(self):
        return str(self.func) + ' Frame'


class TestClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def cool(self, x, t):
        return t.append(1)


def check():
    i = 0  # watchvar i
    y = []  # watchvar y
    c = TestClass(0, y)  # watchvar c.y
    c.y = [1, 2, 3]
    c.cool(i, y)
    j = 0  # watchvar j
    i += 1
    i *= 2
    j = i


def binSearch(arr, t):
    n = len(arr)
    l = 0  # watchvar l
    r = n - 1  # watchvar r
    while (l <= r):
        mid = (r + l) // 2
        if arr[mid] == t:
            return mid
        if arr[mid] > t:
            r = mid - 1
        else:
            l = mid + 1
    return -1


def go():
    print('Started')
    i = 0
    w = Tracer(include_files=['/Users/vishweshdkumar/Desktop/gsoc/finalwork/finalrepo/flowchart_gen/variableTrace'])
    sys.settrace(w.trace)
    # check()
    binSearch([1, 2, 3, 4], 4)
    sys.settrace(None)
    print("ended")
    # sys.settrace(None)


def go_file(*args, **kwargs):
    file = kwargs.pop('file')
    f = kwargs.pop('func')
    include_files = kwargs.pop('include_files')
    w = Tracer(file=file, func=f, include_files=include_files)
    w.run_func(*args, **kwargs)
    pprint(w.changes)
    return w
    # file = "/Users/vishweshdkumar/Desktop/gsoc/tests/baka2.py"
    # f = 'go'
    # file = '/Users/vishweshdkumar/Desktop/gsoc/tests/check_tree.py'
    # f = 'check_full_tree'
    # f = 'check_binary_tree'
    mod_name = Path(file).stem
    spec = importlib.util.spec_from_file_location(mod_name, file)
    mod = importlib.util.module_from_spec(spec)
    file = os.path.abspath(file)  # In case of relative naming
    file_dir = os.path.dirname(file)
    sys.path.append(file_dir)
    # If debugging , set back the original debugger later
    # sys.path.append('/Users/vishweshdkumar/Desktop/gsoc/tests')

    spec.loader.exec_module(mod)
    func = getattr(mod, f, None)

    # import traceback
    # TODO: remove tracing of stdlib functions
    print('Started')
    i = 0

    w = Tracer(include_files=[file_dir])

    # w = Tracer(include_files=['/Users/vishweshdkumar/Desktop/gsoc/tests'])
    # w = Tracer(include_files=['/Users/vishweshdkumar/Desktop/gsoc/finalwork/finalrepo/flowchart_gen/variableTrace'])
    sys.settrace(w.trace)
    # check()
    # binSearch([1, 2, 3, 4], 4)
    func(*args, **kwargs)
    sys.settrace(None)
    print("ended")
    # sys.settrace(None)
    print(w.changes)
    return w


if __name__ == "__main__":
    v = Variable('a', 1, None, None)
    print(v.name)
    # go()
    w = go_file(file='/Users/vishweshdkumar/Desktop/gsoc/tests/baka2.py', func='go')
    # print(w.changers)
    # sys.settrace(None)
