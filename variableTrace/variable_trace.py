# import traceback
# TODO: remove tracing of stdlib functions
import sys
import re
import inspect


# TODO : Need to add function passing logic for mutable objects
class Tracer:
    def __init__(self):
        # Add a global tracer
        self.local_tracers_stack = []  # Stack of local tracers , 1 per frame

    def new_frame(self, frame):
        # TODO
        # add new local tracer for frame
        passed_locals = []
        new_tracer = LocalsTracer()
        if not self.local_tracers_stack:  # First Stack Frame
            self.local_tracers_stack.append(new_tracer)
            return
        old_tracer = self.local_tracers_stack[-1]
        for name, attr, val in zip(old_tracer.names, old_tracer.attrs, old_tracer.vals):
            if self.is_mutable(val):
                for name_new in frame.f_locals:
                    if frame.f_locals[name_new] is val:
                        new_tracer.add(name_new, val, attr)
        print("Variables transfered are", new_tracer.names)
        self.local_tracers_stack.append(new_tracer)
        # Transfer Locals that are transfered with calls (Mutable only)

    def is_mutable(self, obj):
        immutable_types = [bool, int, float, tuple, str, frozenset]
        return type(obj) not in immutable_types

    def trace(self, frame, event, arg):
        if event == "call":
            print("New trace initialized at", frame.f_lineno)
            self.new_frame(frame)
        curr_local_tracer = self.local_tracers_stack[-1]
        curr_local_tracer.trace(frame, event, arg)
        # TODO send params for tracing globally

        # TODO Check for possible changes in return statement(shift this line after check?)
        if event == "return":
            # Remove current tracer from stack
            # TODO check about mmu in this case, should I use del?
            self.local_tracers_stack.pop()
            # Return , as nothing else executed on this statement
            return
        return self.trace


class LocalsTracer:
    def __init__(self):
        # TODO, add functionaly to check multiple variables
        # TODO, add checking in globals
        self.vals = []
        self.names = []
        self.attrs = []
        self.comments = []
        self.lines_comments = {}
        self.toadd = []  # variables parsed from last line comments
        # self.val=self.getval(frame.f_locals)
        self.prev_line = 0
        self.prev_event = "line"

    def add(self, name, val, attr=None):
        self.vals.append(val)
        self.names.append(name)
        self.attrs.append(attr)

    def check(self, f_locals):
        for idx in range(len(self.vals)):
            obj = self.names[idx]
            attr = self.attrs[idx]
            new = self.get_val(obj, attr, f_locals)
            if new != self.vals[idx]:
                print(self.names[idx], "changed on line ", self.prev_line)
            self.vals[idx] = new

    def get_val(self, name, attr, f_locals):
        obj = f_locals[name]
        if attr:
            return getattr(obj, attr)
        else:
            return obj

    def get_comments(self, frame):
        if not frame.f_lineno in self.lines_comments:

            # Extracting source of entire current function
            lines, lineno = inspect.getsourcelines(frame)

            currline = lineno
            for line in lines:
                match = re.match(r"# watchvar (.+)$|^.+# watchvar (.+)$", line)
                comment = None
                if match:
                    comment = match.group(1) or match.group(2)  # Take whichever matches
                    # print(comment)
                self.lines_comments[currline] = comment
                currline += 1
        return self.lines_comments[frame.f_lineno]

    def trace(self, frame, event, arg):
        # Adding variables defined on last line's  comments
        # print(self.toadd,frame.f_lineno,"TOADD")
        # print(self.names,"ADDED")
        while (self.toadd):
            name, attr = self.toadd.pop()
            print("adding Variable", name)
            val = self.get_val(name, attr, frame.f_locals)
            self.add(name, val, attr)
        if event == "line" or event == "return":
            # print(frame.f_locals)
            self.check(frame.f_locals)
            comment = self.get_comments(frame)
            if comment:
                comment = comment.strip()
                # Getting lines to be called added on next step
                parts = comment.split('.')
                if len(parts) == 1:  # implies no attribute defined, a simple variable
                    self.toadd.append((parts[0], None))
                else:
                    self.toadd.append((parts[0], parts[1]))
            self.prev_line = frame.f_lineno
        self.prev_event = event
        return self.trace


class TestClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def cool(self, x, t):
        return self.t.append(1)


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


def go():
    i = 0
    w = Tracer()
    sys.settrace(w.trace)
    check()
    sys.settrace(None)
    # sys.settrace(None)


go()
if __name__ == "__main__":
    go()
    # print(w.changers)
    # sys.settrace(None)