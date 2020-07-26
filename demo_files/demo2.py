import helper


class Solution:
    def __init__(self, matrix):
        self.matrix = matrix
        self.dp  = []
    def findPath(self):
        n, m = len(self.matrix), len(self.matrix[0])
        self.dp = [[0] * m for i in range(n)]  # watchvar self.dp
        self.dp[-1][-1] = 4
        ans = self.hasPath(0, 0)
        helper.DEBUG = 0
        return ans

    def hasPath(self, i, j):
        n, m = len(self.matrix), len(self.matrix[0])
        # helper.dbg(self.dp + [i, j])  # Function call to debug
        if i >= n or i < 0 or j >= m or j < 0:  # Out of bounds
            return False
        if self.matrix[i][j] == 0:
            self.dp[i][j] = 3
            return False
        if self.dp[i][j] == 1:  # Gray
            return False
        if self.dp[i][j] == 3:
            return False
        if self.dp[i][j] == 4:
            return True

        ans = False
        self.dp[i][j] = 1
        right = self.hasPath(i + 1, j)
        left = self.hasPath(i - 1, j)
        up = self.hasPath(i, j + 1)
        down = self.hasPath(i, j - 1)
        ans = right or left or down or up
        self.dp[i][j] = 4 if ans else 3
        return ans


def main():
    s = Solution([[1, 0, 1, 1, 0],
                  [1, 1, 0, 0, 1],
                  [0, 1, 1, 1, 0],
                  [0, 0, 0, 1, 1]])

    s.findPath()
