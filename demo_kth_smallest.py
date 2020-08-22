class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    def __str__(self):
        return str(self.val)
    def rec(self):
        s = str(self.val)
        if self.left:
            s = self.left.rec() + " "+s
        if self.right:
            s += " " + self.right.rec()
        return s
    def __repr__(self):
        return self.__str__()
    def __eq__(self,other):
        if other is None:
            return False
        return self.val == other.val


def kthSmallest(root, k):
    head = root # watchvar btree:left:right:val head
    root # watchvar ref:head:btree root
    stack = [] # watchvar stack
    k # watchvar k
    while root or stack:
        while root:
            stack.append(root)
            root = root.left
        root = stack.pop()
        k -= 1
        if k == 0:
            print(f"Found Root at stack : {stack} , root: {root.val}")
            return root.val
        root = root.right
def go():
    # https://leetcode.com/problems/kth-smallest-element-in-a-bst/
    a = TreeNode(3)
    b = TreeNode(1)
    c = TreeNode(4)
    d = TreeNode(2)
    a.left = b
    b.right = d
    a.right = c
    kthSmallest(a,1)