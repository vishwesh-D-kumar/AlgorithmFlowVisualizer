from pprint import pprint
import os
import ast
from flowgenerator import generate_flow
from staticfg import CFGBuilder, Block, Link
from control_models import DecisionBlock,LoopBlock
import importlib
import sys
from pathlib import Path


class FlowGen:
    def __init__(self, file, func, *args):
        """

        :param file:path to file
        :param func: function to be used
        :param args:args to pass to function
        """

        self.file = file
        self.func = func
        self.args = args
        # Cfg generation
        self.builder, self.cfg = self.get_cfg()
        # Timeline generating parameters
        # List of lines executed on every step
        self.timeline = []
        # Here the main timeline generating function occurs
        self.get_timeline()
        # Alter blocks to corresponding blocks
        self.alter_blocks()
        # Map lines to the blocks they belong to
        self.linesmap = self.map_lines()
        # alter timeline to show used blocks only
        self.timeline = self.alter_timeline()
        pprint(self.linesmap)
        # print(self.timeline)
        # marking visited blocks and cfgs
        self.mark_used_blocks()
        self.mark_used_cfg()

        pprint([(block.used, block.at()) for block in self.cfg.net_blocks])
        self.cfg.net_blocks=[]
        print(self.timeline)

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

    def trace_callback(self, frame, event, arg):
        """
        callback function
        """
        # print(frame.f_code,frame.f_lineno)
        self.timeline.append(frame.f_lineno)
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
        # If debugging , set back the original debugger later
        curr_tracer = sys.gettrace()
        sys.settrace(self.trace_callback)
        func(*self.args)
        sys.settrace(curr_tracer)

    def get_cfg(self):
        """

        Gets cfg built by staticfg, for post processing
        :return builder ,cfg built
        """
        builder = CFGBuilder()
        cfg = builder.build_from_file(self.file, './' + self.file)
        # cfg.build_visual('test1', 'pdf')
        # return cfg
        # cfg.build_visual('test2', 'pdf')
        return builder, cfg

    # Flowchart generating functions
    def alter_timeline(self):
        """
        Function that alters the timeline to only contain lines

        :return: new altered timeline
        """
        new_timeline = []
        # Continue if the line is not mapped to a block, as that means
        # it has no real value in the flow
        for line in self.timeline:
            if line in self.linesmap:
                new_timeline.append(line)
        return new_timeline

    def alter_blocks(self):
        """
        Replaces blocks with corresponding Decion,Loop blocks

        """
        blocks_list = self.cfg.net_blocks[:]  # Copying for safe traversal
        for i in range(len(blocks_list)):
            self.cfg.net_blocks[i] = self.split_block(blocks_list[i])

    def split_block(self, block: Block):
        """

        :param block to be considered for splitting:
        :return: Block to be in main traversal list
        """
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
                    # self.cfg.net_blocks.append(if_block)
                    return block
                else:
                    if_block = DecisionBlock(block.id)
                    self.replace_block(block, if_block)
                    return if_block

                # If blocks are loops , replacing them too
            elif type(block.statements[0]) == ast.While or type(block.statements[0]) == ast.For:
                loop_block = LoopBlock(block.id)
                self.replace_block(block, loop_block)
                return loop_block
        return block

    def replace_block(self, old: Block, new: Block):
        """
        Utility function for replacing old block with new block in cfg
        :param old: block to be replaced
        :param new: block to be replaced with
        :return: None
        """

        new.predecessors = old.predecessors[:]
        for link in new.predecessors:
            link.target = new
            for link_pred in link.source.exits:
                if link_pred.target == old:
                    link_pred.target = new

        new.exits = old.exits[:]
        old.exits = []
        for link in new.exits:
            link.source = new
        new.statements = old.statements[:]
        old.statements = []
        for cfg in self.cfg.functioncfgs.values():
            if cfg.entryblock == old:
                cfg.entryblock = new

    def new_decision_block(self):
        self.builder.current_id += 1
        return DecisionBlock(self.builder.current_id)

    def new_loop_block(self):
        self.builder.current_id += 1
        return LoopBlock(self.builder.current_id)

    # Output generation functions

    def generate_flowchart(self, format='pdf', visual=True):
        """
        Stores flowchart of program in output directory
        :param format: format of produced graph ; svg/pdf..
        :param visual: builds output if true
        :return timeline of blocks
        """
        output_dir = self.create_output_dir()
        # Stores timeline of blocks visited ,for debugging later
        blocks_timeline = []
        # Timeline of links used
        link_used = []
        timeline = self.timeline
        prev_block = self.linesmap[timeline[0]]
        blocks_timeline.append(prev_block)
        link_used_last = None
        i = 0
        for line in timeline:

            # time.sleep(5)
            # If previous block is not the same ,means the block has been changed
            # Only build block if and only the block has changed.
            if line not in self.linesmap:
                continue
            if prev_block != self.linesmap[line]:
                # If link used is None ,implies a function call has happened, and hence no highlight needed
                if link_used_last is not None:
                    link_used_last.used = False
                link_used_last = self.highlight_link_between(prev_block, self.linesmap[line])
                # Build output if visual specified
                if visual:
                    self.cfg.build_visual(f'./{output_dir}/output/{i}', format, show=False)
                blocks_timeline.append(self.linesmap[line])

            prev_block = self.linesmap[line]
            i += 1

        # pprint(blocks_timeline)
        pprint([(block.used, block.at()) for block in blocks_timeline])
        return blocks_timeline

    def map_lines(self):
        """

        :return: dictionary mapping every line to corresponding blocks
        """
        blocks_list = self.cfg.net_blocks
        linesmap = {}
        for block in blocks_list:
            start_statement = block.at()
            end_statement = block.end()
            if start_statement == 1:
                continue
            if end_statement is None and start_statement is not None:
                print("Bug")
            if not end_statement and not start_statement:
                continue
            for i in range(start_statement, end_statement + 1):
                linesmap[i] = block

        return linesmap

    def mark_used_blocks(self):
        """
        function marks which all blocks are visited , and cfgs are visited by algorithm in runtime
        """
        for line in self.timeline:
            block = self.linesmap[line]
            block.used = True

    def mark_used_cfg(self):
        """
        Marks used cfg blocks , to be shown while rendering
        :return:
        """
        self.cfg.used = True  # Used entry CFG
        print("###")
        for func_cfg in self.cfg.functioncfgs.values():
            print(func_cfg.entryblock.at(), func_cfg.entryblock.used)
            # func_cfg.used = True
            func_cfg.used = func_cfg.entryblock.used
        print("###")

    def highlight_link_between(self, node: Block, neigh: Block):
        # print(node, neigh)
        """

        :param node: previously executed block
        :param neigh: currently executed block
        :return: link between node and neigh , if it exist ,else None
        """
        for link in node.exits:
            if link.target == neigh:
                link.used = True
                print("####", link)
                return link
        return None


if __name__ == "__main__":
    f = FlowGen('test.py', 'main')
    # arr = [1,2,3,4,5,6]
    # f = FlowGen("test_files/sorts.py","selection_sort",arr) #Sorted the array in place
    timeline = f.generate_flowchart('pdf', True)
    # print("Arr after sorting :",arr)
    # input("Array has been sorted! Press any key to continue")
    # f = FlowGen("test_files/searches.py","binarySearch",arr,6) #Searching via binary search
    # timeline = f.generate_flowchart('pdf',True)
    # f = FlowGen('test.py', 'f4',[1,2,3,4,5])
    # f = FlowGen("test_files/recursion.py", "knapSack", 5, [2, 4], [13, 4], 2)
    # f = FlowGen('test_files/simple_loop.py','break_test')
    # timeline = f.generate_flowchart('pdf', True)

    print("Executed")
