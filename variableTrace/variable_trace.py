# import traceback
#TODO: remove tracing of stdlib functions
#TODO : Add support for imports using dll library, by deepcopying globals
import sys
class VarWatcher:
    def __init__(self,name,attr,frame):
        #TODO, add functionaly to check multiple variables
        self.name=name
        self.attr=attr
        self.val=self.getval(frame.f_locals)
        self.prev_line=frame.f_lineno
        # print("initialized")
    def getval(self,local_frame):
        # print(local_frame)
        obj=local_frame[self.name]
        if self.attr:
            return getattr(obj,attr)
        else:
            return obj
    def check(self,local_frame):
        new_val=self.getval(local_frame)
        if new_val!=self.val:
            print("Changed",self.name,self.prev_line)
        return new_val
    def trace(self,frame,event,arg):
        # print(frame.f_locals)
        # print(event)
        if event=="line" or event=="return":
            if self.name in frame.f_locals:
                self.val=self.check(frame.f_locals)
            self.prev_line=frame.f_lineno
        return self.trace

def check():
    i=0
    i+=1
    i*=2

def go():
    i=0
    w = VarWatcher('i',None,sys._getframe(0))
    sys.settrace(w.trace)
    check()

    sys.settrace(None)

    # print(w.changers)
    # sys.settrace(None)
go()