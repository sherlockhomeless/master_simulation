import unittest
from task import Task
from process import Process


class TestProcess(unittest.TestCase):

    def test_process_lateness(self):
        # Test if earliness works correctly
        t_1: Task = Task(10, 0, 0, length_real=5)
        t_1.run(5)
        t_2: Task = Task(10, 0, 0, length_real=10)
        t_2.run(5)

        p: Process = Process([t_1, t_2], 0)
        p.update_lateness()
        self.assertEqual(-5, p.lateness)

        # Test if on time is correct
        t_1: Task = Task(5, 0, 0, length_real=5)
        t_1.run(5)

        p: Process = Process([t_1], 0)
        p.update_lateness()
        self.assertEqual(0, p.lateness)

        # Test if lateness is correct
        t_1: Task = Task(5, 0, 0, length_real=5)
        t_1.run(5)
        t_2: Task = Task(5, 0, 0, length_real=20)
        t_2.run(20)
        p: Process = Process([t_1, t_2], 0)
        p.update_lateness()
        self.assertEqual(15, p.lateness)
