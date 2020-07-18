from graphviz import Digraph

import inspect
import copy


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


class VisualTree:
    def __init__(self, **kwargs):

        self.root_name = kwargs.pop('name')
        self.root_node = get_obj(kwargs.pop('frame'), self.root_name)  ##Setting self.root_node
        self.kwargs = kwargs
        self.graph = None
        self.node_count = 1
        self.references = []  # Referers for rendering
        self.val = kwargs.pop('val')
        self.left = kwargs.pop('left')
        self.right = kwargs.pop('right')
        self.deepcopy_head = self.copy_tree(self.root_node)
        # self.graph.node('somehash',label="Link",_attributes={'URL': 'https://github.com/vishwesh-D-kumar/AlgorithmFlowVisualizer/blob/master/LEGEND.png','pos':'-1000,-1000!'})
        # node.attr

    def copy_tree(self, root):
        if root is None:
            return None
        print(root.val, end=" ")

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
        for label, referer in self.references:
            if curr_node is referer:
                self.node_count += 1
                self.graph.node(str(self.node_count), label=label, _attributes={'shape': 'plaintext'})
                self.graph.edge(str(self.node_count), str(parentnum), "Points To")
        if getattr(curr_node, self.left) is not None:
            self.graph.node(str(self.node_count + 1), str(getattr(getattr(curr_node, self.left), self.val)))
            self.graph.edge(str(self.node_count + 1), str(parentnum), label="Left")
            self.node_count += 1
            self.traverseTree(getattr(curr_node, self.left))
        if getattr(curr_node, self.right) is not None:
            self.graph.node(str(self.node_count + 1), str(getattr(getattr(curr_node, self.right), self.val)))
            self.graph.edge(str(self.node_count + 1), str(parentnum), label="Right")
            self.node_count += 1
            self.traverseTree(getattr(curr_node, self.right))

    # def get_referer_obj(self, referer):
    #     return referer[1].f_locals.get(referer[0])

    def render(self):

        self.graph = Digraph(**self.kwargs)
        self.graph.node(str(self.node_count), str(self.root_node.val))
        # print(self.graph.source)
        self.traverseTree(self.root_node)
        self.graph.render('tree', view=True)

    def add_referer(self, var_name, var_frame):
        self.references.append([var_name, get_obj(var_frame, var_name)])

    def check(self):
        self.check_node(self.root_node, self.deepcopy_head)
        self.copy_tree(self.root_node)
        self.render()

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


class Node:
    def __init__(self, val):
        self.val = val
        self.right = None
        self.left = None

if __name__ == "__main__":

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

    newTree = VisualTree(name='root', comment='Tree A', frame=inspect.currentframe(), format='pdf', left='left',
                         right='right', val='val')
    newTree.render()
    input()
    # newTree.add_referer('currNode', inspect.currentframe())
    root.left = None
    newTree.check()
    # newTree.render()
