import unittest
import os
from connect import *


class NotCompoundedTest(unittest.TestCase):
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
        expected_blocks = [15,16,18,15,16,18,15,16,15,16,18,15]
        for actual, expected in zip(timeline, expected_blocks):
            self.assertEqual(actual.at(), expected)

if __name__ == '__main__':
    unittest.main()
