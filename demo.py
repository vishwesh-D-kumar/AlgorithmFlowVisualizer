from variableTrace.variable_trace import go_file
from recursion_visualize.stackgen import go

#Run variable tracing demo on pathfinding algo
go_file([
    [1, 0, 1, 1, 0],
    [1, 1, 0, 0, 1],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 1, 1]

], file='demo_files/demo1.py', func='go',include_files = ['demo_files/demo2.py'])

#Run Tree Demo on bst insertion
go_file(file='demo_files/tree_demo.py', func='main',include_files=[])

# Run Stack visualization demo on pathfinding algo via dfs
go([
    [1, 0, 1, 1, 0],
    [1, 1, 0, 0, 1],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 1, 1]

], file='demo_files/demo1.py', func='go')
