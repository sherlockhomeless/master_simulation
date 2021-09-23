import unittest

import config
from task import Task
from plan import Plan
from process_runner import ProcessRunner
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
                counts[new_task.length_real] = counts[new_task.length_real]+1
            except KeyError:
                counts[new_task.length_real] = 1

        real_values = [0 for x in range(200)]
        for key in counts:
            real_values[key] = counts[key]

        y = np.array(real_values)
        plt.bar(range(0, 200), y)
        if False:
            plt.show()

    def test_share_slot(self):
        t1, t2, t3 = Task(1, 0, 0), Task(1, 0, 1), Task(1, 0, 2)
        ins = 1
        # p = Plan.generate_custom_plan((t1, t2, t3))
        t1.preempt(t2)
        t1.run(ins)
        self.assertTrue(t1.slot == t2)
        self.assertEqual(t1.instructions.instructions_retired_task, ins)
        self.assertEqual(t1.instructions.instructions_retired_slot, 0)
        self.assertEqual(t1.slot.instructions.instructions_retired_slot, ins)

        t1.preempt(t3)

        self.assertEqual(t1.slot, t3)
        self.assertEqual(t2.slot, t3)

    def test_run(self):
        config.set_test_config()
        config.T1_MIN_TICKS_OFF = 1
        config.T1_MAX_VALUE = 100
        t0 = Task(1000, 0, 0, length_real=1200)
        t1 = Task(2000, 0, 1, length_real=2000)
        p = Plan.generate_custom_plan([t0, t1])
        pr = ProcessRunner(p)
        pr.run()

        assert t0.instruction_counter.instructions_task == 1200
        assert t0.instruction_counter.instructions_slot == 1100
        assert t1.instruction_counter.instructions_task == 2000
        assert t1.instruction_counter.instructions_slot == 2100

    def test_preempt(self):
        t0, t1, t2 = Task(100, 0, 0), Task(100, 0, 1), Task(100, 0, 2)
        t0.preempt(t1)

        self.assertTrue(t0.was_preempted is True)
        self.assertTrue(t0.times_preempted == 0)
        self.assertTrue(t1.times_preempted == 1)
        self.assertTrue(t1.shares_slot_with == [t0])

        t0, t1, t2 = Task(100, 0, 0), Task(100, 0, 1), Task(100, 0, 2)
        t0.preempt(t1)
        t0.preempt(t2)

        self.assertTrue(t2.times_preempted == 2)
        self.assertTrue(t2.shares_slot_with == [t0, t1])
        self.assertTrue(t1.shares_slot_with == [t0])








