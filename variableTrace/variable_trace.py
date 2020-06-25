# import traceback
import dill
#TODO: remove tracing of stdlib functions
#TODO : Add support for imports using dll library, by deepcopying globals
import sys
class VarWatcher:
    def __init__(self):
        #TODO, add functionaly to check multiple variables
        #TODO, add checking in globals
        self.objs=[]
        self.vals=[]
        self.names=[]
        self.attrs=[]
        # self.val=self.getval(frame.f_locals)
        self.prev_line=frame.f_lineno
        # print("initialized")
    def add(self,variable,name,val,attr=None):
        self.objs.append(variable)
        self.vals.append(val)
        self.names.append(name)
        self.attrs.append(attrs)
    def getval(idx):
        # print(local_frame)
        obj=self.objs[idx]
        attr=self.attr[idx]
        # obj=local_frame[self.name]
        if self.attr:
            return getattr(obj,attr)
        else:
            return obj
    def check(self):
        for i in range(len(self.vals)):
            new=getval(idx)
            if new!=self.vals[idx]:
                print(self.names[idx],"changed on line ",self.prev_line)
            self.vals[idx]=new
    def check_comment(self,line):
        #TODO
        pass
    def trace(self,frame,event,arg):
        # print(frame.f_locals)
        # print(event)
        if event=="line" or event=="return":
              self.check()
              self.prev_line=frame.f_lineno
        return self.trace

def check():
    i=0
    i+=1
    i*=2

def go():
    i=0
    w = VarWatcher()
    sys.settrace(w.trace)
    check()

    sys.settrace(None)
    # print(w.changers)
    # sys.settrace(None)
go()
