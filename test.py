def f(x, t):
    l = 0
    r = len(x) - 1
    while (l <= r):
        mid = (l + r) // 2  # vardbg: ref x[mid]
        print(x[mid])
        if x[mid] < min(x):
            continue
        if x[mid] > t:
            r = mid - 1  # vardbg: ref x[r]
        else:
            l = mid + 1  # vardbg: ref x[l]
        if x[mid] < min(x):
            continue
    return r

def f2(arr):
    n=len(arr)
    for i in range(n):
        for j in range(n):
            if i==j:
                break
            print(i,j)
        if i<j:
            print(i,j)
            break
    print("Got here")
def f3():
    if a:
        if b:
            print("0")
        elif c == d:
            print("1")
        else:
            print(2)
    elif b == a:
        print("3")
    else:
        print(5)

def f4(x):
    for i in range(len(x)):
        if i==1:
            print("1")
        else:
            break
    print("End")

# def f1(a):
#     if a:
#         if a+1:
#             print("1")
#         else:
#             print("2")
#     else:
#         print("4")

# def foo():
#     i = 0
#     while True:
#         i += 1
#         break
#     for j in range(3):
#         i += j
#         break
#     return i


def main():
    l = 1
    f([1, 3, 4, 5, 6, 10, 11], 6)


if __name__ == "__main__":
    main()
