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


def main():
    print(lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]))


if __name__ == '__main__':
    main()
