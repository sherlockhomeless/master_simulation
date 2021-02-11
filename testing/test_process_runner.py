import unittest

import config
from process_runner import ProcessRunner
from plan import Plan
import task
import thresholder


task.ips = config.INS_PER_TICK


class TestProcessRunner(unittest.TestCase):
    def set_up(self):
        ipt = 100000
        thresholder.ipt = ipt
        task.ipt = ipt
        thresholder.consumable_buffer = 1
        thresholder.max_ticks_off_t1 = 1
        thresholder.max_relative_deviation_t1 = 1
        thresholder.reschedule_time = 0
        thresholder.cap_lateness = 2
        thresholder.spacer_constant = 1
        config.COST_CONTEXT_SWITCH = 1
        self.new_plan = Plan.read_plan_from_file(self.path_log)
        self.pr = ProcessRunner.get_process_runner(self.new_plan)
        self.pr.ipt = ipt

    def test_search_task_following(self):
        self.path_log = "testing/plan_preempt.log"
        self.set_up()
        next_id = self.pr.search_task_following(0)
        self.assertEqual(1, next_id)
        next_id = self.pr.search_task_following(7)
        self.assertEqual(8, next_id)


    def test_t1_is_triggering(self):
        self.path_log = "testing/plan_preempt.log"
        self.set_up()
        self.pr.run_tick()
        change = self.pr.tracking.change_log
        self.assertTrue(self.pr.vrm.get_last_signal() is None)

        self.pr.run_tick()
        change_task_preempt = change[-2]
        change_new_task = change[-1]
        self.assertTrue(change_task_preempt.type_event == "t1")
        self.assertTrue(change_new_task.type_event == "task_start")


    def test_preemption(self):
        """
        Check if the process runner signals early finishing tasks
        """
        self.path_log = "testing/plan_preempt.log"
        self.set_up()
        plan = self.pr.plan
        t = self.pr.cur_task
        start_index = plan.index(t)

        self.pr.run_tick()
        self.pr.run_tick()

        preempt_index = plan.index(t)
        self.assertTrue( start_index != preempt_index)
        # task0 should have been preempted and moved in front of the task with id 5


        # [TODO] check if preemted task only gets time as planed for next task

    def test_finishing_early_signal(self):
        """
        Sets Task up to finish to early and checks if a signal was sent to VRM
        """


        self.setUp()
        cur_task_id = self.pr.cur_task
        self.pr.cur_task.length_real = 1
        self.pr.cur_task.length_plan = 10**10

        self.pr.run_tick()

        self.assertEqual(self.pr.vrm.get_last_signal(), cur_task_id)
        z = 0


if __name__ == '__main__':
    unittest.main()
