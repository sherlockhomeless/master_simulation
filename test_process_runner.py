import unittest
from process_runner import ProcessRunner
from plan import Plan
import sim
import task

task.ips = sim.INS_PER_TICK


class TestProcessRunner(unittest.TestCase):
    def setUp(self):
        self.new_plan = Plan.read_plan_from_file("testing/plan.log")
        self.pr = ProcessRunner.get_process_runner(self.new_plan)

    def test_preemption(self):
        all_indices_of_process_0 = []
        for i, task in enumerate(self.runner.plan):
            if task.process_id == 0:
                all_indices_of_process_0.append(i)

        # check if the task is moved to the correct index

        plan = self.runner.plan
        will_be_preemted_task = plan[all_indices_of_process_0[0]]
        will_be_preemted_task.length_real = will_be_preemted_task.length_plan * 2

        # [TODO] check if preemted task only gets time as planed for next task


if __name__ == '__main__':
    unittest.main()
