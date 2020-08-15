def for_loop():
    for i in range(4):
        i -= 1
    return


def break_test():
    i = 0
    while (i < 5):
        if i == 4:
            break
        i += 1

def continue_test():
    for i in range(4):
        if i==2:
            continue
        print("Done")