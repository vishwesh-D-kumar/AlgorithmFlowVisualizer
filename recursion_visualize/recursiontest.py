def f(i):
    return g()+1
def g():
    return 1
def main():
    s=1
    # print(f(1))
    print(rec(5))
def rec(i):
    if i==0:return 0
    return rec(i-1)+1

if __name__=="__main__":
    main()