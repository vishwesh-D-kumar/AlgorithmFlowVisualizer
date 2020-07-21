def lengthOfLIS(arr) -> int:
    def lis(i):
        if i == n:
            return 0
        if dp[i] != -1:
            return dp[i]
        ans = 1
        for j in range(i + 1, n):
            if arr[j] > arr[i]:
                lisj = lis(j)
                ans = max(ans, 1 + lisj)
        dp[i] = ans
        return dp[i]

    n = len(arr) + 1
    dp = [-1] * n
    arr = [float("-inf")] + arr
    return lis(0) - 1


def findPath(matrix):
    n, m = len(matrix), len(matrix[0])
    dp = [[0] * m for i in range(n)]
    dp[-1][-1] = 4
    def get_neighbours(i, j):
        neighbours = []
        for x, y in [i + 1, j], [i, j + 1], [i - 1, j], [i, j - 1]:
            if n > x >= 0 and 0 <= y < m:
                neighbours.append((x, y))
        return neighbours

    def hasPath(i, j):
        print(i,j)
        for __ in dp:
            print(__)
        if matrix[i][j] == 0:
            dp[i][j] = 3
            return False
        if dp[i][j] == 1: # Gray
            return False
        if dp[i][j] == 3:
            return False
        if dp[i][j] == 4:
            return True
        neighbours = get_neighbours(i, j)
        # print(neighbours,'##')
        ans = False
        dp[i][j] = 1
        for x, y in neighbours:
            if hasPath(x, y):
                ans = True
        dp[i][j] = 4 if ans else 3
        return ans

    return hasPath(0, 0)


def main():
    # print(lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]))

    matrix = [
        [1, 0, 1, 1, 0],
        [1, 1, 0, 0, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 1]

    ]
    print(findPath(matrix))


if __name__ == '__main__':
    main()
