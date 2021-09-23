import unittest

import config
from process_runner import ProcessRunner
from plan import Plan
from task import Task
from process import Process
import task

task.ips = config.INS_PER_TICK

def create_test_pr(list_ids: [(int, int),...]) -> ProcessRunner:
    """
    :param list_ids: Tuple of (task_id, process_id)
    :return: ProcessRunner with Tasks for list_ids as plan
    """
    tasks = []
    for id in list_ids:
        tasks.append(Task(1, id[1], id[0]))
    processes = []
    num_processes = max([t[1] for t in list_ids])
    for i in range(num_processes):
        processes.append(Process(list(filter(lambda t: t.process_id == i, tasks)), 0))
    p = Plan(tasks, processes)
    return ProcessRunner(p)


class TestProcessRunner(unittest.TestCase):

    def set_up(self, plan_name):
        config.COST_CONTEXT_SWITCH = 0
        config.LOG_TERM = True
        config.INS_PER_TICK = 100000
        self.test_plan_path = "/home/ml/Dropbox/Master-Arbeit/code/threshold_simulation/testing/"
        self.new_plan = Plan.read_plan_from_file(self.test_plan_path + plan_name)
        self.pr = ProcessRunner.get_process_runner(self.new_plan)

    def test_search_task_following(self):
        plan_path = "plan_preempt.log"
        self.set_up(plan_path)
        next_id = self.pr.search_task_following(0)
        self.assertEqual(1, next_id)
        next_id = self.pr.search_task_following(7)
        self.assertEqual(8, next_id)


    def test_finishing_early_signal(self):
        """
        Sets Task up to finish to early and checks if a signal was sent to VRM
        """
        config.set_test_config()
        t0 = Task(10000, 0, 0, length_real=100)
        t1 = Task(100, 0, 1, length_real=500)
        p = Plan.generate_custom_plan([t0, t1])
        pr = ProcessRunner.get_process_runner(p)

        pr.run_tick()
        self.assertTrue(pr.job_sched.get_last_signal()[1] is t0)

    def test_assign_new(self):
        """
        Intended scenario: Task is late, unallocated slot is reassigned
        :return:
        """
        t0 = Task(1000, 0, 0, length_real=1500)
        t1 = Task(5000, -1, -1)
        p = Plan.generate_custom_plan([t0, t1])
        pr = ProcessRunner.get_process_runner(p)

        pr.run()
        self.assertEqual(len(pr.finished_tasks), 1)
        self.assertTrue(pr.finished_tasks[0].finished_late)

    def test_move_preempted(self):
        t0, t1, t2 = Task(100, 0, 0), Task(100, 1, 1), Task(100, 0, 2)
        t3, t4 = Task(100, 1, 3), Task(100, 0, 4)
        p0, p1 = Process([t0, t2, t4], 0), Process([t1, t3], 0)
        pl = Plan([t0, t1, t2, t3, t4], [p0, p1])
        pr = ProcessRunner(pl)

        pr.move_preempted_task(t0, 2)
        self.assertTrue(pr.task_list[:3] == [t1, t0, t2])

        pr.task_list = pr.task_list[1:]
        pr.move_preempted_task(t0, 3)
        self.assertEqual(pr.task_list, [t3, t0, t2, t4])

    def test_find_slot_for_preemption(self):
        tasks_ids = ((0,0), (1,1), (2,1), (3,0))
        pr = create_test_pr(tasks_ids)
        slot = pr.find_slot_for_preemption(1)
        self.assertEqual(slot, 3)


    def test_preempt_current_task(self):
        pass




