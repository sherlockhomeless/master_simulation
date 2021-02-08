import unittest
from process_runner import ProcessRunner
from plan import Plan
import sim
import task
import thresholder

task.ips = sim.INS_PER_TICK


class TestProcessRunner(unittest.TestCase):
    def setUp(self):
        self.new_plan = Plan.read_plan_from_file("testing/plan.log")
        self.pr = ProcessRunner.get_process_runner(self.new_plan)



    def test_preemption(self):
        """
        Check if the process runner signals early finishing tasks
        """
        raise NotImplementedError
        all_indices_of_process_0 = []
        for i, task in enumerate(self.runner.plan):
            if task.process_id == 0:
                all_indices_of_process_0.append(i)

        # check if the task is moved to the correct index

        plan = self.runner.plan
        will_be_preemted_task = plan[all_indices_of_process_0[0]]
        will_be_preemted_task.length_real = will_be_preemted_task.length_plan * 2

        # [TODO] check if preemted task only gets time as planed for next task

    def test_finishing_early_signal(self):
        """
        Sets Task up to finish to early and checks if a signal was sent to VRM
        """
        thresholder.consumable_buffer = 1
        thresholder.max_task_deviation_t1 = 1
        thresholder.max_relative_deviation = 1
        thresholder.reschedule_time = 0
        thresholder.ipt = 2
        thresholder.cap_lateness = 2
        thresholder.spacer_constant = 1
        self.setUp()
        cur_task_id = self.pr.cur_task
        self.pr.cur_task.length_real = 1
        self.pr.cur_task.length_plan = 10**10

        self.pr.run_tick()

        self.assertEqual(self.pr.vrm.get_last_signal(), cur_task_id)
        z = 0







if __name__ == '__main__':
    unittest.main()
