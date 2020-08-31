import demo2
import helper

# Question : is there a path from 0,0(top,left) to (n,m)
# in this given matrix of dimensions n*m?.
# matrix[i][j]==1 shows that the block can be visited ,and a 0 implies an obstacle lies there.
# Demonstrated via dfs.

def go(matrix):
    # Showcasing Global tracing across modules
    helper.DEBUG = 1  # watchvar helper.DEBUG
    sol = demo2.Solution(matrix)
    ans = sol.findPath()

    # Things left
    # Check for variable deletion locally
    # Check for global variables existence

def main():
    matr = [[1, 0, 0],
            [1, 1, 1]]
    go(matr)

if __name__ == "__main__":
    main()
    # print("Done")