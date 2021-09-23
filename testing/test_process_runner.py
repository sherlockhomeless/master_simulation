import unittest

import config
from process_runner import ProcessRunner
from plan import Plan
from task import Task
from process import Process
import task


task.ips = config.INS_PER_TICK


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

    def test_preemption(self):
        """
        Check if process preepption is working correctly
        Task is set to be planned to finish at 1, buf finishes at some huge amount
        -> should trigger at MIN_TICKS_OFF
        -> check if it is pushed to next task of slot
        """

        # --- SETUP ---

        t_00 = Task(100, 0, 0, length_real=300)
        t_01 = Task(100, 1, 1, length_real=100)
        t_02 = Task(100, 0, 2, length_real=200)
        t_03 = Task(500, 1, 3, length_real=1000)
        t_04 = Task(1000, 0, 4, length_real=1000)

        config.INS_PER_TICK = 100
        config.T1_MIN_TICKS_OFF = 1
        config.update()

        plan = Plan.generate_custom_plan([t_00, t_01, t_02, t_03, t_04])

        self.pr = ProcessRunner.get_process_runner(plan)
        start_task = self.pr.cur_task
        other_task_of_p = self.pr.task_list[2]

        # time 0-100
        self.pr.run_tick()
        cur_task = self.pr.cur_task
        self.assertTrue(start_task.shares_slot_with == [])
        self.assertTrue(cur_task is start_task)
        self.assertTrue(self.pr.t1 == start_task.length_plan_unchanged + config.NO_PREEMPTION)

        # time 100 - 200 -> should now have been preempted, 0 instructions run on next task
        self.pr.run_tick()
        cur_task = self.pr.cur_task
        self.assertTrue(cur_task is not start_task)
        self.assertTrue(cur_task.instruction_counter.instructions_task == 0)

        # time 200 - 300 -> t01 should finish
        self.pr.run_tick()
        cur_task = self.pr.cur_task
        self.assertTrue(cur_task is start_task)
        self.assertTrue(start_task.shares_slot_with[0] is other_task_of_p)
        self.assertTrue(len(self.pr.task_list) == 4)

        # time 300-400, rerun first task & finished first task
        self.pr.run_tick()
        cur_task = self.pr.cur_task
        self.assertTrue(cur_task is other_task_of_p)
        self.assertTrue(self.pr.t1 == other_task_of_p.length_plan + config.NO_PREEMPTION)
        self.assertTrue(start_task.instruction_counter.instructions_task == 300)
        self.assertTrue(start_task.instruction_counter.instructions_slot == 200)
        self.assertTrue(start_task.task_finished is True)
        self.assertTrue(other_task_of_p.task_finished is False)
        self.assertTrue(len(self.pr.task_list) == 3)

        # time 400-500, t02 should start
        self.pr.run_tick()
        cur_task = self.pr.cur_task
        self.assertTrue(cur_task is t_03)
        self.assertTrue(other_task_of_p.shares_slot_with[0] is t_04)

        all_instructions_run = sum([x.instruction_counter.instructions_task for x in (t_00, t_01, t_02, t_03)])
        self.assertTrue(all_instructions_run == self.pr.tick_counter)

    def test_multi_stack_preemption(self):
        t0 = Task(100, 0, 0, length_real=500)
        t1 = Task(100, 0, 1, length_real=500)
        t2 = Task(500, 0, 2, length_real=500)

        p = Plan.generate_custom_plan([t0, t1, t2])
        config.INS_PER_TICK = 100
        config.T1_MIN_TICKS_OFF = 1
        config.LOG = False
        config.update()
        pr = ProcessRunner.get_process_runner(p)
        # time 0-100, -> run t0
        pr.run_tick()
        cur_task = pr.cur_task
        self.assertTrue(cur_task is t0)

        # time 100-200 -> t0 is preempted
        pr.run_tick()
        cur_task = pr.cur_task
        self.assertTrue(cur_task.shares_slot_with[0] == t1)

        # t2 slot should start at 2x preemption limit => 400 with double stack
        pr.run_tick()
        pr.run_tick()

        # should be preempted again here
        self.assertTrue(t0.shares_slot_with == [t1, t2])
        self.assertTrue(t1.shares_slot_with == [t2])
        self.assertTrue(t0.get_instructions_cur_slot() == 0)
        self.assertTrue(t0.instruction_counter.instructions_slot == 200)
        self.assertTrue(t1.instruction_counter.instructions_slot == 200)

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

    def test_find_preemption_slot(self):
        t0, t1, t2 = Task(100, 0, 0), Task(100, 1, 1), Task(100, 0, 2)
        p0, p1 = Process([t0, t2], 0), Process([t1], 0)
        pl = Plan([t0, t1, t2], [p0, p1])
        pr = ProcessRunner(pl)



