from pprint import pprint
import os
import ast
from flowgenerator import generate_flow
from staticfg import CFGBuilder, Block, Link
import importlib
import sys
from pathlib import Path

class DecisionBlock(Block):
    """
    A block for non loop control flow statements
    """

    def __init__(self, id):
        super().__init__(id)
        self.shape = "diamond"


class LoopBlock(Block):
    """
    A block for loop statements
    """

    def __init__(self, id):
        super().__init__(id)
        self.shape = "oval"





class FlowGen:
    def __init__(self,file,func):
        """

        :param file:path to file
        :param func: function to be used
        """

        self.file=file
        self.func=func
        #Cfg generation
        self.builder,self.cfg= self.get_cfg()
        #Timeline generating parameters
        #Set of lines to leave
        self.leave=self.cfg.lines_to_leave
        #List of lines executed on every step
        self.flow=[]
        #Here the main timeline generating function occurs
        self.get_timeline()

        #Alter blocks to corresponding blocks
        self.alter_blocks()
        self.linesmap=self.map_lines()




    def create_output_dir(self):
        """
        Creates a output directory
        :return output directory path
        """
        output_dir = os.path.dirname(f'./{self.file}')
        try:
            os.mkdir(f'./{output_dir}/output')
        except:
            pass
        return output_dir
    def trace_callback(self,frame,event,arg):
        """
        callback function
        """
        if not frame.f_lineno in self.leave:
            self.flow.append(frame.f_lineno)
        return self.trace_callback

    def get_timeline(self):
        """
        saves the timeline of the program
        """

        mod_name = Path(self.file).stem
        spec = importlib.util.spec_from_file_location(mod_name, self.file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        func = getattr(mod, self.func, None)
        sys.settrace(self.trace_callback)
        func()
        sys.settrace(None)


    def get_cfg(self):
        """

        Gets cfg built by staticfg, for post processing
        :return builder ,cfg built
        """
        builder = CFGBuilder()
        cfg = builder.build_from_file(self.file, './' + self.file)
        cfg.build_visual('test1', 'pdf')
        # return cfg
        # cfg.build_visual('test2', 'pdf')
        return builder,cfg

    #Flowchart generating functions

    def alter_blocks(self):
        """
        Replaces blocks with corresponding Decion,Loop blocks

        """
        blocks_list = self.cfg.net_blocks[:]#Copying for safe traversal
        for block in blocks_list:
            self.split_block(block)



    def split_block(self,block: Block):
        if block.statements:
            if type(block.statements[-1]) == ast.If:
                # Adding a new Block ,if there are more than 1 statements
                if len(block.statements) > 1:
                    print("New if Block")

                    if_block = self.new_decision_block()
                    if_statement = block.statements[-1]
                    block.statements.remove(if_statement)
                    if_block.statements.append(if_statement)
                    if_block.exits = block.exits[:]
                    for link in if_block.exits:
                        link.source = if_block
                    block.exits = []
                    block.exits.append(Link(block, if_block))
                else:
                    self.replace_block(block, DecisionBlock(block.id))
                # If blocks are loops , replacing them too
            elif type(block.statements[0]) == ast.While or type(block.statements[0]) == ast.For:
                self.replace_block(block, LoopBlock(block.id))

    def replace_block(self,old: Block, new: Block):
        """
        Utility function for replacing old block with new block in cfg
        :param old: block to be replaced
        :param new: block to be replaced with
        :return: None
        """
        for link in old.predecessors[:]:
            link.target = new

        new.exits = old.exits[:]
        old.exits = []
        for link in new.exits:
            link.source = new
        new.statements = old.statements

    def new_decision_block(self):
        self.builder.current_id += 1
        return DecisionBlock(self.builder.current_id)

    def new_loop_block(self):
        self.builder.current_id += 1
        return LoopBlock(self.builder.current_id)

    #Output generation functions

    def generate_flowchart(self,format):
        """
        Stores flowchart of program in output directory
        :param format: format of produced graph ; svg/pdf..
        """
        output_dir=self.create_output_dir()
        # Stores timeline of blocks visited ,for debugging later
        blocks_timeline = []
        timeline= self.flow
        prev_block = self.linesmap[timeline[0]]
        link_used_last = None
        i = 0
        for line in timeline:
            self.cfg.build_visual(f'./{output_dir}/output/{i}', format, show=False)
            # time.sleep(5)
            # If previous block is not the same ,means the block has been changed
            if prev_block != self.linesmap[line]:
                # If link used is None ,implies a function call has happened, and hence no highlight needed
                if link_used_last is not None:
                    link_used_last.used = False
                link_used_last = self.highlight_link_between(prev_block, self.linesmap[line])

            prev_block = self.linesmap[line]
            i += 1
            blocks_timeline.append(self.linesmap[line])
        pprint(blocks_timeline)
    def map_lines(self):
        """

        :return: dictionary mapping every line to corresponding blocks
        """
        blocks_list=self.cfg.net_blocks
        linesmap = {}
        for block in blocks_list:
            start_statement = block.at()
            end_statement = block.end()
            if end_statement is None and start_statement is not None:
                print("Bug")
            if not end_statement and not start_statement:
                continue
            for i in range(start_statement, end_statement + 1):
                linesmap[i] = block
        return linesmap

    def highlight_link_between(self,node: Block, neigh: Block):
        # print(node, neigh)
        """

        :param node: previously executed block
        :param neigh: currently executed block
        :return: link between node and neigh , if it exist ,else None
        """
        for link in node.exits:
            if link.target == neigh:
                link.used = True
                # print("####", link)
                return link
        return None
f= FlowGen('test.py','main')
f.generate_flowchart('svg')


