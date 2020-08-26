class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    def __str__(self):
        s = str(self.val)
        if self.left:
            s = str(self.left) + " "+s
        if self.right:
            s += " " + str(self.right)
        return s
    def __repr__(self):
        return self.__str__()
    def __eq__(self,other):
        return self.__str__() == other.__str__()

  
def inorderTraversal(root):
    head = root # watchvar btree:left:right:val head
    root # watchvar ref:head:btree root
    res = [] # watchvar res
    stack = [] # watchvar stack
    node = None # watchvar ref:head:btree node
    while True:
        while root: 
            stack.append(root)
            root = root.left
        if not stack:
            return res
        node = stack.pop()
        res.append(node.val)
        root = node.right

def go():
	# https://leetcode.com/problems/binary-tree-inorder-traversal/
	a = TreeNode(1)
	b = TreeNode(2)
	c = TreeNode(3)
	d = TreeNode(4)
	a.right = b
	b.left = c
	b.right = d
	ans= inorderTraversal(a)