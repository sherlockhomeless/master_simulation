import unittest
from task import Task
from job_scheduler import *


class TestTracker(unittest.TestCase):

    def test_reschedule_simple(self):
        # testing shrink
        t0 = Task(100, 0, 0)
        t_list = [t0]
        t_list_rescheduled = JobScheduler.reschedule_simple(t_list, shrink=True)
        self.assertTrue(t_list_rescheduled[0].length_plan == 95)
        # test stretch
        t0 = Task(100, 0, 0)
        t_list = [t0]
        t_list_rescheduled = JobScheduler.reschedule_simple(t_list)
        self.assertTrue(t_list_rescheduled[0].length_plan == 105)