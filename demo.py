from variableTrace.variable_trace import go_file
from recursion_visualize.stackgen import go

go_file([
    [1, 0, 1, 1, 0],
    [1, 1, 0, 0, 1],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 1, 1]

], file='demo_files/demo1.py', func='go',include_files = ['demo_files/demo2.py'])

# go([
#     [1, 0, 1, 1, 0],
#     [1, 1, 0, 0, 1],
#     [0, 1, 1, 1, 0],
#     [0, 0, 0, 1, 1]
#
# ], file='demo_files/demo1.py', func='go')
