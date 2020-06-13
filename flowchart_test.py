import unittest
import os
from connect import *


class BasicTest(unittest.TestCase):
    def test_loop(self):
        f = FlowGen("test_files/simple_loop.py", "for_loop")
        timeline = f.generate_flowchart(visual=False)
        expected_blocks = [2, 3, 2, 3, 2, 3, 2, 3, 2, 4]
        for actual, expected in zip(timeline, expected_blocks):
            self.assertEqual(actual.at(), expected)
        # timeline = f.generate_flowchart('pdf',False)
        # f = FlowGen(os.getscwd()+'/test_files/simple_loop.py','for_loop')

    def test_break(self):
        f = FlowGen("test_files/simple_loop.py", "break_test")
        timeline = f.generate_flowchart(visual=False)
        expected_blocks = [8, 9, 10, 12, 9, 10, 12, 9, 10, 12, 9, 10, 12, 9, 10]
        for actual, expected in zip(timeline, expected_blocks):
            self.assertEqual(actual.at(), expected)

    def test_continue(self):
        f = FlowGen("test_files/simple_loop.py", "continue_test")
        timeline = f.generate_flowchart(visual=False)
        expected_blocks = [15, 16, 18, 15, 16, 18, 15, 16, 15, 16, 18, 15]
        for actual, expected in zip(timeline, expected_blocks):
            self.assertEqual(actual.at(), expected)


class SortingTests(unittest.TestCase):
    def test_selection_sort(self):
        f = FlowGen("test_files/sorts.py", "selection_sort", [64, 25, 12, 22])
        timeline = f.generate_flowchart(visual=False)
        expected_blocks = [2,6, 10, 11, 12, 13, 11, 12, 13, 11, 12, 11, 17]
        for actual, expected in zip(timeline, expected_blocks):
            self.assertEqual(actual.at(), expected)
    def test_insertion_sort(self):
        f = FlowGen("test_files/sorts.py", "insertionSort", [4,3,2])
        timeline = f.generate_flowchart(visual=False)
        expected_blocks = [2, 22, 24, 30, 31, 30, 33, 22, 24, 30, 31, 30, 31, 30, 33, 22]
        for actual, expected in zip(timeline, expected_blocks):
            self.assertEqual(actual.at(), expected)
class DPTests(unittest.TestCase):
    def test_knapsack(self):
        f = FlowGen("test_files/recursion.py", "knapSack",5, [2, 4],[13, 4],2)
        timeline = f.generate_flowchart(visual=False)
        expected_blocks=[2, 5, 6, 7, 8, 6, 7, 8, 6, 7, 8, 6, 7, 8, 6, 7, 8, 6, 7, 8, 6, 5, 6, 7, 8, 6, 7, 9, 13, 6, 7, 9, 10, 6, 7, 9,
         10, 6, 7, 9, 10, 6, 7, 9, 10, 6, 5, 6, 7, 8, 6, 7, 9, 13, 6, 7, 9, 13, 6, 7, 9, 13, 6, 7, 9, 10, 6, 7, 9, 10,
         6, 5, 15]
        for actual, expected in zip(timeline, expected_blocks):
            self.assertEqual(actual.at(), expected)



if __name__ == '__main__':
    unittest.main()
