def f(i):
    return g() + 1


def g():
    return 1


def main():
    s = 1
    # print(f(1))
    # print(f(rec(5)))
    # f2(1)
    conditional_test(5)


def f2(i):
    print(i)
    i += 1


def rec(i):
    if i == 0: return 0
    return rec(i - 1) + 1


def conditional_test(a):
    if (a == 2):
        print(2)
    elif (a == 3):
        print(3)
    else:
        print(4)

    print(3)


if __name__ == "__main__":
    main()
