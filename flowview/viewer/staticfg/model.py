"""
Control timeline graph for Python programs.
"""
# Aurelien Coet, 2018.

import ast
import astor
import graphviz as gv

class Block(object):
    """
    Basic block in a control timeline graph.

    Contains a list of statements executed in a program without any control
    jumps. A block of statements is exited through one of its exits. Exits are
    a list of Links that represent control timeline jumps.
    """

    __slots__ = ["id", "statements", "func_calls", "predecessors", "exits","shape",'used','color']

    def __init__(self, id):
        # Id of the block.
        self.id = id
        # Statements in the block.
        self.statements = []
        # Calls to functions inside the block (represents context switches to
        # some functions' CFGs).
        self.func_calls = []
        # Links to predecessors in a control timeline graph.
        self.predecessors = []
        # Links to the next blocks in a control timeline graph.
        self.exits = []
        #Stores the graph shape in which to be rendered
        self.shape = "rect"
        #Storing list of blocks to map later
        # block_list.append(self)
        #Shows whether block is used in runtime
        self.used = False
        self.color = "lightblue"


    def __str__(self):
        if self.statements:
            return "block:{}@{}".format(self.id, self.at())
        return "empty block:{}".format(self.id)

    def __repr__(self):
        txt = "{} with {} exits".format(str(self), len(self.exits))
        if self.statements:
            txt += ", body=["
            txt += ", ".join([ast.dump(node) for node in self.statements])
            txt += "]"
        return txt

    def at(self):
        """
        Get the line number of the first statement of the block in the program.
        """
        if self.statements and self.statements[0].lineno >= 0:
            return self.statements[0].lineno
        return None

    def end(self):
        """
        Get the line number where the function ends
        :return:
        """
        if self.statements and self.statements[-1].lineno >= 0:
            return self.statements[-1].lineno
        return None

    def is_empty(self):
        """
        Check if the block is empty.

        Returns:
            A boolean indicating if the block is empty (True) or not (False).
        """
        return len(self.statements) == 0

    def get_source(self):
        """
        Get a string containing the Python source code corresponding to the
        statements in the block.

        Returns:
            A string containing the source code of the statements.
        """
        src = ""
        for statement in self.statements:
            if type(statement) in [ast.If, ast.For, ast.While]:
                src += (astor.to_source(statement)).split('\n')[0] + "\n"
            elif type(statement) == ast.FunctionDef or \
                    type(statement) == ast.AsyncFunctionDef:
                src += (astor.to_source(statement)).split('\n')[0] + "...\n"
            else:
                src += astor.to_source(statement)
        return src

    def get_calls(self):
        """
        Get a string containing the calls to other functions inside the block.

        Returns:
            A string containing the names of the functions called inside the
            block.
        """
        txt = ""
        for func_name in self.func_calls:
            txt += func_name + '\n'
        return txt


class Link(object):
    """
    Link between blocks in a control timeline graph.

    Represents a control timeline jump between two blocks. Contains an exitcase in
    the form of an expression, representing the case in which the associated
    control jump is made.
    """

    __slots__ = ["source", "target", "exitcase", "used"]

    def __init__(self, source, target, exitcase=None):
        #Changed class checking to isinstance checking to allow for subclassing of blocks
        assert isinstance(source,Block), "Source of a link must be a block or its subclass"
        assert isinstance(target,Block), "Target of a link must be a block or its subclass"
        # Block from which the control timeline jump was made.
        self.source = source
        # Target block of the control timeline jump.
        self.target = target
        # 'Case' leading to a control timeline jump through this link.
        self.exitcase = exitcase
        # defines whether link used in runtime or not
        self.used = False

    def __str__(self):
        return "link from {} to {}".format(str(self.source), str(self.target))

    def __repr__(self):
        if self.exitcase is not None:
            return "{}, with exitcase {}".format(str(self),
                                                 ast.dump(self.exitcase))
        return str(self)

    def get_exitcase(self):
        """
        Get a string containing the Python source code corresponding to the
        exitcase of the Link.

        Returns:
            A string containing the source code.
        """
        if self.exitcase:
            return astor.to_source(self.exitcase)
        return ""


class CFG(object):
    """
    Control timeline graph (CFG).

    A control timeline graph is composed of basic blocks and links between them
    representing control timeline jumps. It has a unique entry block and several
    possible 'final' blocks (blocks with no exits representing the end of the
    CFG).
    """

    def __init__(self, name, asynchr=False):
        assert type(name) == str, "Name of a CFG must be a string"
        assert type(asynchr) == bool, "Async must be a boolean value"
        # Name of the function or module being represented.
        self.name = name
        # Type of function represented by the CFG (sync or async). A Python
        # program is considered as a synchronous function (main).
        self.asynchr = asynchr
        # Entry block of the CFG.
        self.entryblock = None
        # Final blocks of the CFG.
        self.finalblocks = []
        # Sub-CFGs for functions defined inside the current CFG.
        self.functioncfgs = {}
        #Defines whether cfg used in runtime
        self.used = False

    def __str__(self):
        return "CFG for {}".format(self.name)

    def _visit_blocks(self, graph, block, visited=[], calls=True):
        #If block unused in runtime , continue
        # if not block.used:
        #     return
        # Don't visit blocks twice.
        if block.id in visited:
            return

        nodelabel = block.get_source()

        #Using shape paramater to change shape of block
        if block.used:
            graph.node(str(block.id), label=nodelabel,shape=block.shape,fillcolor=block.color)
        visited.append(block.id)

        # Show the block's function calls in a node.
        if calls and block.func_calls and block.used:
            calls_node = str(block.id) + "_calls"
            calls_label = block.get_calls().strip()
            graph.node(calls_node, label=calls_label,
                       _attributes={'shape': 'box3d'})
            graph.edge(str(block.id), calls_node, label="calls",
                       _attributes={'style': 'dashed'})

        # Recursively visit all the blocks of the CFG.
        for exit in block.exits:
            self._visit_blocks(graph, exit.target, visited, calls=calls)
            edgelabel = exit.get_exitcase().strip()
            #Only draw links if the corresponding exits are being utilsed
            if exit.target.used and block.used:
                graph.edge(str(block.id), str(exit.target.id), label=edgelabel, color="red" if exit.used else "black")

    def _build_visual(self, format='pdf', calls=True):
        graph = gv.Digraph(name='cluster' + self.name, format=format,
                           graph_attr={'bgcolor':'transparent'},
                           node_attr={ 'style': 'filled'},
                           edge_attr={'color':'white'}
                           )
        # graph.attr(colorscheme='greys85',bgcolor="grey11")
        # graph.attr(style='filled', fillcolor='5')

        self._visit_blocks(graph, self.entryblock, visited=[], calls=calls)

        # Build the subgraphs for the function definitions in the CFG and add
        # them to the graph.
        for subcfg in self.functioncfgs:
            if self.functioncfgs[subcfg].used:
                # print("Yes",subcfg)
                subgraph = self.functioncfgs[subcfg]._build_visual(format=format,
                                                               calls=calls)
                graph.subgraph(subgraph)

        return graph

    def build_visual(self, filepath, format, calls=True, show=True):
        """
        Build a visualisation of the CFG with graphviz and output it in a DOT
        file.

        Args:
            filename: The name of the output file in which the visualisation
                      must be saved.
            format: The format to use for the output file (PDF, ...).
            show: A boolean indicating whether to automatically open the output
                  file after building the visualisation.
        """
        graph = self._build_visual(format, calls)
        graph.render(filepath, view=show)

    def __iter__(self):
        """
        Generator that yields all the blocks in the current graph, then
        recursively yields from any sub graphs
        """
        visited = set()
        to_visit = [self.entryblock]

        while to_visit:
            #TODO : either use a deque for this , or pop() , to avoid o(n) complexity of pop
            block = to_visit.pop(0)
            visited.add(block)
            for exit_ in block.exits:
                if exit_.target in visited or exit_.target in to_visit:
                    continue
                to_visit.append(exit_.target)
            yield block

        for subcfg in self.functioncfgs.values():
            yield from subcfg
