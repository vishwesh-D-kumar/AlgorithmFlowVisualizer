from staticfg import builder
import importlib.util
from pathlib import Path
import sys
from pprint import pprint
import os
import ast
from flowgenerator import generate_flow
from staticfg import CFGBuilder, Block, Link
import time
import tempfile

filepath = "test.py"
jsonout = 'f.json'
defaultfunc = "main"


# Adding subclasses of blocks for better functionality

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


def get_cfg():
    """

    :return: cfg built by staticfg
    """
    builder = CFGBuilder()
    cfg = builder.build_from_file(filepath, './' + filepath)
    cfg.build_visual('test1', 'pdf')
    # return cfg

    blocks_list = cfg.net_blocks[:]
    for block in blocks_list:
        split_block(block, builder)

    cfg.build_visual('test2', 'pdf')
    return cfg


def get_block_scope():
    """

    :return: scope of block ie: start and end line of block
    """
    return block.at(), block.end()


def highlight_link_between(node: Block, neigh: Block):
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


def split_block(block: Block, builder: CFGBuilder):
    # TODO

    if len(block.statements):
        if type(block.statements[-1]) == ast.If:
            # Adding a new Block ,if there are more than 1 statements
            if len(block.statements) > 1:
                print("New if Block")

                if_block = new_decision_block(builder)
                if_statement = block.statements[-1]
                block.statements.remove(if_statement)
                if_block.statements.append(if_statement)
                if_block.exits = block.exits[:]
                for link in if_block.exits:
                    link.source = if_block
                block.exits = []
                block.exits.append(Link(block, if_block))
            else:
                replace_block(block, DecisionBlock(block.id))
            # If blocks are loops , replacing them too
        elif type(block.statements[0]) == ast.While or type(block.statements[0]) == ast.For:
            replace_block(block, LoopBlock(block.id))


def replace_block(old: Block, new: Block):
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
    new.statements=old.statements


def new_decision_block(builder: CFGBuilder):
    builder.current_id += 1
    return DecisionBlock(builder.current_id)

    # pass


def new_loop_block(builder: CFGBuilder):
    builder.current_id += 1
    return LoopBlock


if __name__ == "__main__":

    cfg = get_cfg()
    # Net blocks of cfg
    blocks_list = cfg.net_blocks

    # Timeline of lines
    timeline = generate_flow(filepath, defaultfunc, cfg.lines_to_leave)
    print(timeline)

    linesmap = {}
    # Create directory for storing files
    # TODO,Merge all svgs/pdfs into a single pdf

    output_dir = os.path.dirname(f'./{filepath}')
    try:
        os.mkdir(f'./{output_dir}/output')
    except:
        pass
    block: Block  # Type hint
    # Mappign lines to their corresponding blocks
    for block in blocks_list:
        start_statement = block.at()
        end_statement = block.end()
        if end_statement is None and start_statement is not None:
            print("Bug")
        if not end_statement and not start_statement:
            continue
        for i in range(start_statement, end_statement + 1):
            linesmap[i] = block
    pprint(linesmap)
    # Stores timeline of blocks visited ,for debugging later
    blocks_timeline = []
    prev_block = linesmap[timeline[0]]
    link_used_last = None
    i = 0
    for line in timeline:
        cfg.build_visual(f'./{output_dir}/output/{i}', 'svg', show=False)
        # time.sleep(5)
        # If previous block is not the same ,means the block has been changed
        if prev_block != linesmap[line]:
            # If link used is None ,implies a function call has happened, and hence no highlight needed
            if link_used_last is not None:
                link_used_last.used = False
            link_used_last = highlight_link_between(prev_block, linesmap[line])

        prev_block = linesmap[line]
        i += 1

        blocks_timeline.append(linesmap[line])
    pprint(blocks_timeline)
