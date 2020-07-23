import demo2
import helper


def go(matrix):
    # Showcasing Global tracing across modules
    helper.DEBUG = 1  # watchvar helper.DEBUG
    sol = demo2.Solution(matrix)
    ans = sol.findPath()

    # Things left
    # Check for variable deletion locally
    # Check for global variables existence

def main():
    go([[1, 0, 1, 1, 0],
        [1, 1, 0, 0, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 1]])

if __name__ == "__main__":
    main()
    # print("Done")
