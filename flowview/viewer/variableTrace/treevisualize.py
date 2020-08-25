from graphviz import Digraph

import inspect
import copy
step_count = 0  #tree steps, a static variable to prevent overlaps on

def get_obj(frame, name):
    try:
        return frame.f_locals.get(name)
    except KeyError as e:
        try:
            return frame.f_globals.get(name)
        except KeyError as e:
            print("No such variable found ")  # Variable has been removed for sure , ie the node no longer exists
            raise e


class DeepCopyNode:
    __slots__ = ['left', 'right', 'val']

    def __init__(self):
        self.left = None
        self.right = None
        self.val = None


class DeepCopyNodeFull:
    __slots__ = ['child', 'val']

    def __init__(self):
        self.child = []
        self.val = None


class VisualTree:
    def __init__(self, **kwargs):

        self.name = kwargs.pop('name')
        self.root_node = kwargs.pop('obj')
        # self.root_node = get_obj(kwargs.pop('frame'), self.name)  ##Setting self.root_node
        self.kwargs = kwargs
        self.graph = None
        self.obj_val = self.root_node
        self.node_count = 1
        self.references = []  # Referers for rendering
        self.val = kwargs.pop('val')
        self.left = kwargs.pop('left')
        self.right = kwargs.pop('right')
        self.deepcopy_head = self.copy_tree(self.root_node)
        self.is_global = False
        self.step_count = 0
        # self.graph.node('somehash',label="Link",_attributes={'URL': 'https://github.com/vishwesh-D-kumar/AlgorithmFlowVisualizer/blob/master/LEGEND.svg','pos':'-1000,-1000!'})
        # node.attr

    def copy_tree(self, root):
        if root is None:
            return None
        # print(root.val, end=" ")

        copy_node = DeepCopyNode()
        try:
            copy_node.val = copy.deepcopy(getattr(root, self.val))  # Allowing for deepcopying of values
        except:
            # TODO : lessen except clause
            copy_node.val = getattr(root, self.val)

        # getattr(root,self.val),getattr(root,self.left),getattr(root,self.right))
        copy_node.left = self.copy_tree(getattr(root, self.left))
        copy_node.right = self.copy_tree(getattr(root, self.right))
        return copy_node

    def traverseTree(self, curr_node):
        # Inorder traversal of tree
        parentnum = self.node_count
        for var in self.references:
            if curr_node is var.val:
                self.node_count += 1
                self.graph.node(str(self.node_count), label=var.name, _attributes={'shape': 'doublecircle','fillcolor':'lightblue4'})
                self.graph.edge(str(self.node_count), str(parentnum), "Points To")
        if getattr(curr_node, self.left) is not None:
            self.graph.node(str(self.node_count + 1), str(getattr(getattr(curr_node, self.left), self.val)))
            self.graph.edge(str(parentnum),str(self.node_count + 1), label=self.left)
            self.node_count += 1
            self.traverseTree(getattr(curr_node, self.left))
        if getattr(curr_node, self.right) is not None:
            self.graph.node(str(self.node_count + 1), str(getattr(getattr(curr_node, self.right), self.val)))
            self.graph.edge(str(parentnum),str(self.node_count + 1), label=self.right)
            self.node_count += 1
            self.traverseTree(getattr(curr_node, self.right))

    # def get_referer_obj(self, referer):
    #     return referer[1].f_locals.get(referer[0])

    def render(self):
        global step_count
        self.kwargs['graph_attr']={'bgcolor':'transparent'}
        self.kwargs['node_attr'] = {'style':'filled','fillcolor':'lightblue'}
        self.graph = Digraph(**self.kwargs)
        self.graph.attr(label= "Graph of variable: "+self.name)
        self.graph.node(str(self.node_count), str(getattr(self.root_node, self.val)))
        # print(self.graph.source)
        self.traverseTree(self.root_node)
        output_dir = 'flowview/viewer/static'
        self.graph.render(f'{output_dir}/tree/{self.name}{step_count}',format='svg')

        # self.graph.render(f'viewer/static/tree/{self.name}{step_count}',format='svg')
        filename = f'{output_dir}/tree/{self.name}{step_count}.svg'
        step_count += 1
        return filename

    def add_referrer(self,var):
        print("REFERRER ADDED", "$%")
        for var_there in self.references:
            if var.name == var_there.name:
                return 
        self.references.append(var)

    def check(self, frame, prev_line):
        # self.check_node(self.root_node, self.deepcopy_head)
        # self.copy_tree(self.root_node)

        print(self.root_node,'Check this',prev_line)
        return self.render()


    def check_node(self, root1, root2):
        if root1 is None and root2 is None:
            return True
        if root1 is None or root2 is None:
            print(f"Change detected from {root2} to {root1}")
            return False
        # if root1 is None:
        #     if root2 is None:
        #         return True
        #     else:
        #         print(f"Change detected from {getattr(root2)} to {getattr(root1)}")
        #         return False
        # if root2 is None:
        #     print(f"Change detected from {getattr(root2)} to {getattr(root1)}")
        #     return False
        left1, left2 = getattr(root1, self.left), root2.left
        right1, right2 = getattr(root1, self.right), root2.right
        if getattr(root1, self.val) != root2.val:
            print(f"Change detected from {root2.val} to {getattr(root1, self.val)}")
            return False
        return self.check_node(left1, left2) and self.check_node(right1, right2)


class FullVisualTree:
    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        # self.root_node = get_obj(kwargs.pop('frame'), self.name)  ##Setting self.root_node
        self.root_node = kwargs.pop('obj')
        self.kwargs = kwargs
        self.graph = None
        self.node_count = 1
        self.references = []  # Referers for rendering
        self.val = kwargs.pop('val')
        self.child = kwargs.pop('child')
        self.obj_val = None
        # print(self.kwargs)
        print(self.val, self.child, type(self.root_node), "$%$%")
        # self.deepcopy_head = self.copy_tree(self.root_node)
        self.is_global = False
        self.step_count = 0
    def copy_tree(self, root):
        if root is None:
            return None
        print(getattr(root, self.val), end=" ")

        copy_node = DeepCopyNodeFull()
        try:
            copy_node.val = copy.deepcopy(getattr(root, self.val))  # Allowing for deepcopying of values
        except:
            # TODO : lessen except clause
            copy_node.val = getattr(root, self.val)

        # getattr(root,self.val),getattr(root,self.left),getattr(root,self.right))
        for v in getattr(root, self.child):
            copy_node.child.append(self.copy_tree(v))
        return copy_node

    def check(self, frame, prev_line):
        return self.render()

    def check_node(self, root1, root2):
        pass
        # if root1 is None and root2 is None:
        #     return True
        # if root1 is None or root2 is None:
        #     print(f"Change detected from {root2} to {root1}")
        #     return False
        # children1 = sorted(getattr(root1,self.child)) #Sorting to ensure order in checking
        # children2 = sorted(root2.child)
        #
        # if getattr(root1, self.val) != root2.val:
        #     print(f"Change detected from {root2.val} to {getattr(root1, self.val)}")
        #     return False
        # i=0
        # ans = True
        # for v1,v2 in zip(children1,children2):
        #     i += 1
        #     if not self.check_node(v1,v2):
        #         ans = False
        # if len(children1)>len(children2):
        #     print(f"Nodes Added with parent node {root1}")
        #     for v in children1:
        #
        #
        # # for i in range(max(len(children1),len(children2))):
        #
        #
        #
        # # return self.check_node(left1, left2) and self.check_node(right1, right2)

    def render(self):
        global step_count
        self.kwargs['graph_attr']={'bgcolor':'transparent'}
        self.kwargs['node_attr'] = {'style':'filled','fillcolor':'lightblue'}
        self.graph = Digraph(**self.kwargs)
        self.graph.attr(label= self.name)
        self.traverseTree(self.root_node)
        # print(self.graph.source)
        output_dir = 'flowview/viewer/static'
        self.graph.render(f'{output_dir}/tree/{self.name}{step_count}',format='svg')
        # filename = f'{self.name}{step_count}.svg'
        filename = f'{output_dir}/tree/{self.name}{step_count}.svg'
        step_count += 1
        return filename

    def traverseTree(self, root):
        # print(type(self))
        self.graph.node(str(self.node_count), str(getattr(root, self.val)))
        # print(self.graph.source)
        parentnum = self.node_count

        for name, watcher in self.references:
            if watcher is root:
                self.node_count += 1
                self.graph.node(str(self.node_count), name)
                self.graph.edge(str(self.node_count), str(parentnum))

        for v in getattr(root, self.child):
            self.node_count += 1
            child_num = self.node_count
            self.traverseTree(v)
            self.graph.edge(str(parentnum),str(child_num))


class Node:
    def __init__(self, val):
        self.val = val
        self.right = None
        self.left = None


class FullNode:
    def __init__(self, val):
        self.data = val
        self.children = []


def check_binary_tree():
    root = Node(1)
    left = Node(2)
    right = Node(3)
    leffleft = Node(4)
    lefRight = Node(5)
    righRight = Node(6)
    root.left = left
    root.right = right
    root.left.left = leffleft
    root.left.right = lefRight
    root.right.right = righRight
    currNode = lefRight

    newTree = VisualTree(name='root', comment='Tree A', obj=root, format='pdf', left='left',
                         right='right', val='val')
    newTree.render()
    input()
    # newTree.add_referer('currNode', inspect.currentframe())
    root.left = None
    newTree.check()
    newTree.render()


def check_full_tree():
    root = FullNode(1)
    child1 = FullNode(2)
    child2 = FullNode(3)
    child3 = FullNode(4)
    child4 = FullNode(5)
    child5 = FullNode(6)
    root.children.extend([child1, child2, child3, child4, child5])
    child11 = FullNode(7)
    child12 = FullNode(8)
    child31 = FullNode(9)
    child1.children.extend([child11, child12])
    child3.children.append(child31)
    newTree = FullVisualTree(name='root', comment='Tree B', obj=root, val='data', child='children', format='pdf')
    newTree.render()


if __name__ == "__main__":
    check_binary_tree()
    check_full_tree()
