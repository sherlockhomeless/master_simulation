import unittest
from task import Task
import task
import matplotlib.pyplot as plt
import numpy as np


class TestTask(unittest.TestCase):
    def test_Task(self):
        task.ips = 1
        task.sigma = 10

        center = 100

        counts = {}

        for x in range(50000):
            new_task = Task(center, 0, 0)
            try:
                counts[new_task.length_real]= counts[new_task.length_real]+1
            except KeyError:
                counts[new_task.length_real] = 1

        real_values = [0 for x in range(200)]
        for key in counts:
            real_values[key] = counts[key]

        print(real_values)
        y = np.array(real_values)
        plt.bar(range(0,200), y)
        plt.show()

    def test_share_slot(self):
        t1, t2, t3 = Task(1, 0, 0), Task(1, 0, 1), Task(1, 0, 2)
        t1.preempt(t2)

        self.assertTrue(len(t1.shares_slot_with) == 1)
        self.assertTrue(t2.shares_slot is True)
        self.assertTrue(t2.shares_slot_with == [])

        t1.preempt(t3)

        self.assertTrue(len(t1.shares_slot_with) == 2)
        self.assertTrue(len(t2.shares_slot_with) == 1)
        self.assertTrue(len(t3.shares_slot_with) == 0)






