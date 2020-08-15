def binarySearch(arr, t):
    l = 0
    r = len(arr) - 1
    while (l <= r):
        mid = l + (r - l) // 2

        if arr[mid] == t:
            return mid
        if arr[mid] > t:
            r = mid - 1
        else:
            l = mid + 1
    return -1
