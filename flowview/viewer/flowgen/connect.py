from pprint import pprint
import os
import ast
# from flowgenerator import generate_flow
from ..staticfg import CFGBuilder, Block, Link
from .control_models import DecisionBlock,LoopBlock
import importlib.util
import sys
from pathlib import Path
import abc
ALLOWED_EVENTS = {"call", "line", "return"}
DISALLOWED_FUNC_NAMES = {"<genexpr>", "<listcomp>", "<dictcomp>", "<setcomp>"}
STDLIB_DIR = Path(abc.__file__).parent
COMPLETE_FLOW  = True


class FlowGen:
    def __init__(self, file, func,include_files, *args):
        """

        :param file:path to file
        :param func: function to be used
        :param args:args to pass to function
        """

        self.file = file
        self.func = func
        self.args = args
        self.stdlib_cache = {}
        self.block_image_cache= {}
        self.blocks_to_cfg = {}
        self.cfg_file_cache = {}
        self.linesmap = {}
        self.include_files = [os.path.abspath(file).lower() for file in include_files] 
        # Cfg generation
        self.timeline = []

        self.get_timeline()
        self.builder, self.cfg = self.get_cfg(self.file)
        # Timeline generating parameters
        # List of lines executed on every step

        # Here the main timeline generating function occurs
        
        # alter timeline to show used blocks only
        # self.timeline = self.alter_timeline()
        # print(self.timeline)
        # marking visited blocks and cfgs
        # self.mark_used_cfg()
        
        pprint([(block.used, block.at()) for block in self.cfg.net_blocks])
        print(self.timeline)
        self.final_dict= {}

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

    def create_output_dir(self):
        """
        Creates a output directory
        :return output directory path
        """
        output_dir = 'flowview/viewer/static'
        # print(os.path.abspath(output_dir),"Output directory")
        return output_dir
        output_dir = os.path.dirname(f'{self.file}')
        # print(os.path.dirname('viewer/apps.py'),"LETS GO")
                # output_dir = 'viewer/output'
        try:
            os.mkdir(f'{output_dir}/output')
        except:
            pass
        return output_dir
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
            # print(curr_file,self.include_files)
            return True in [curr_file.startswith(included_file.lower()) for included_file in self.include_files]
        return True
    def trace_callback(self, frame, event, arg):
        """
        callback function
        """
        # print(frame.f_code,frame.f_lineno)
        if not self.check_in_path(frame):
            return
        self.timeline.append((frame.f_lineno,os.path.abspath(frame.f_code.co_filename)))
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

    def get_cfg(self,filename):
        """

        Gets cfg built by staticfg, for post processing
        :return builder ,cfg built
        """
        if filename in self.cfg_file_cache:
            self.file = filename
            builder,cfg = self.cfg_file_cache[filename]
            self.cfg = cfg
            self.builder = builder
            return self.cfg_file_cache[filename]
        builder = CFGBuilder()
        cfg = builder.build_from_file(filename,filename)
        # cfg.build_visual('test1', 'pdf')
        # return cfg
        # cfg.build_visual('test2', 'pdf')
        self.file = filename
        self.cfg_file_cache[filename] = builder,cfg
        self.cfg = cfg
        self.builder = builder
        # Alter blocks to corresponding blocks
        self.alter_blocks()
        # Map lines to the blocks they belong to
        self.linesmap.update(self.map_lines())
        self.mark_used_blocks()
        self.map_blocks_cfg()
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
            else:
                print(f"Removed line : {line}")
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
                    if_block.predecessors.append(Link(block,if_block))
                    self.cfg.net_blocks.append(if_block)
                    return block
                else:
                    if_block = DecisionBlock(block.id)
                    self.replace_block(block, if_block)
                    self.cfg.net_blocks.append(if_block)
                    return if_block

                # If blocks are loops , replacing them too
            elif type(block.statements[0]) == ast.While or type(block.statements[0]) == ast.For:
                loop_block = LoopBlock(block.id)
                self.replace_block(block, loop_block)
                self.cfg.net_blocks.append(loop_block)
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

    def generate_flowchart(self, format='svg', visual=True):
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
        # prev_block = self.linesmap[timeline[0]]
        prev_block = None
        blocks_timeline.append(prev_block)
        link_used_last = None
        i = 1
        self.cfg.build_visual(f'{output_dir}/flowchart/{i}', format='svg', show=False)
        last_file = f'{output_dir}/flowchart/{i}.svg'
        main_file = last_file
        # for cfg in self.cfg.functioncfgs:
        #     cfg.used = False
        for line,file in timeline:
            i+=1
            self.get_cfg(os.path.abspath(file))
            # time.sleep(5)
            # If previous block is not the same ,means the block has been changed
            # Only build block if and only the block has changed.
            self.final_dict[i] = {'images':last_file,'line':line,'file':file}
            if (line,file) not in self.linesmap:
                
                self.final_dict[i]['images']=last_file
                self.final_dict[i]['line'] = line
                continue
            if prev_block != self.linesmap[line,file]: #line,file
                # If link used is None ,implies a function call has happened, and hence no highlight needed
                if link_used_last is not None:
                    link_used_last.used = False
                link_used_last = self.highlight_link_between(prev_block, self.linesmap[line,file])
                # Build output if visual specified
                if visual:
                    self.final_dict[i]['images'] = f'{output_dir}/flowchart/{i}.svg'
                    self.final_dict[i]['line'] = line
                    curr_block = self.linesmap[line,file] #line,file
                    print(curr_block.at(),line,self.cfg.used,i,line,"#$#")
                    if curr_block not in self.blocks_to_cfg:
                        self.final_dict[i]['images'] = main_file
                    elif (curr_block,link_used_last) in self.block_image_cache:
                        self.final_dict[i]['images'] = self.block_image_cache[(curr_block,link_used_last)]
                    else:
                        curr_cfg = self.blocks_to_cfg[curr_block]
                        curr_cfg.used = True
                        curr_block.is_curr = True
                        if not COMPLETE_FLOW:
                            self.activate_current_blocks(curr_block,True)
                        self.cfg.build_visual(f'{output_dir}/flowchart/{i}', format='svg', show=False) # cfgmap
                        curr_cfg.used = False
                        if not COMPLETE_FLOW:
                            self.activate_current_blocks(curr_block,False)
                        curr_block.is_curr = False
                        self.block_image_cache[(curr_block,link_used_last)] = f'{output_dir}/flowchart/{i}.svg'
                        # curr_block.used = False
                    last_file = self.final_dict[i]['images']
                blocks_timeline.append(self.linesmap[line,file])
            else:
                self.final_dict[i]['images'] = last_file
                self.final_dict[i]['line'] = line
            prev_block = self.linesmap[line,file]
        # pprint(blocks_timeline)
        dbg = []
        for block in blocks_timeline:
            if block is not None:
                dbg.append((block.used, block.at()))
        pprint(dbg)
        return blocks_timeline
    def activate_current_blocks(self,curr_block,active):
        curr_block.used = active
        for exit in curr_block.exits:
            neighbour_block = exit.target
            neighbour_block.used = active
        for predecessor in curr_block.predecessors:
            prev_neighbour = predecessor.source
            prev_neighbour.used = active


    def map_blocks_cfg(self):
        self.blocks_to_cfg.update({block:self.cfg for block in self.cfg})
        # blocks_to_cfg = {}
        for funccfg in self.cfg.functioncfgs:
            for block in self.cfg.functioncfgs[funccfg]:
                self.blocks_to_cfg[block] = self.cfg.functioncfgs[funccfg]
        
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
                linesmap[i,self.file] = block

        return linesmap

    def mark_used_blocks(self):
        """
        function marks which all blocks are visited , and cfgs are visited by algorithm in runtime
        """
        for line,file in self.timeline:
            if (line,file) in self.linesmap:
                block = self.linesmap[line,file]
                block.used = True

    def mark_used_cfg(self):
        """
        Marks used cfg blocks , to be shown while rendering
        :return:
        """
        self.cfg.used = True  # Used entry CFG
        # print("###")
        for func_cfg in self.cfg.functioncfgs.values():
            print(func_cfg.entryblock.at(), func_cfg.entryblock.used)
            # func_cfg.used = True
            func_cfg.used = func_cfg.entryblock.used
        # print("###")

    def highlight_link_between(self, node: Block, neigh: Block):
        # print(node, neigh)
        """

        :param node: previously executed block
        :param neigh: currently executed block
        :return: link between node and neigh , if it exist ,else None
        """
        if node is None:
            return None
        for link in node.exits:
            if link.target == neigh:
                link.used = True
                print("####", link)
                return link
        return None
from io import StringIO
class OutputRecorder:

    def __init__(self,filename,func,include_files):
        self.final_dict = {}
        self.step = 1
        self.include_files = [os.path.abspath(file).lower() for file in include_files] 
        self.record = StringIO()
        self.stdlib_cache = {}
        self.file = filename
        self.func = func
    def record_output(self,*args):
        old_stdout = sys.stdout
        sys.stdout = self.record
        mod_name = Path(self.file).stem
        spec = importlib.util.spec_from_file_location(mod_name, self.file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        func = getattr(mod, self.func, None)
        # If debugging , set back the original debugger later
        curr_tracer = sys.gettrace()
        sys.settrace(self.trace_callback)
        func(*args)
        sys.settrace(curr_tracer)
        sys.stdout = old_stdout
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
            # print(curr_file,self.include_files)
            return True in [curr_file.startswith(included_file.lower()) for included_file in self.include_files]
        return True
    def trace_callback(self,frame,event,arg):

        if not self.check_in_path(frame):
            return
        self.final_dict[self.step] = self.record.getvalue()
        self.step+=1
        return self.trace_callback

if __name__ == "__main__":
    # print("Yes")
    # f = FlowGen('test.py', 'main')
    #Example instantiation
    arr = [1,2,3,4,5,6]
    f = FlowGen("test_files/searches.py","binarySearch",arr,6) #Searching via binary search
    timeline = f.generate_flowchart('pdf',True)
    ######
    # input("Array has been sorted! Press any key to continue")

    # f = FlowGen('test.py', 'f4',[1,2,3,4,5])
    # f = FlowGen("test_files/recursion.py", "knapSack", 5, [2, 4], [13, 4], 2)
    # f = FlowGen('test_files/simple_loop.py','break_test')
    # f = FlowGen("test_files/sorts.py", "selection_sort", [64, 25, 12, 22])
    # timeline = f.generate_flowchart('pdf', True)
    print("Executed")