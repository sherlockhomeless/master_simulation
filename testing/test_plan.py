import unittest
from plan import Plan
from task import Task
from process import Process
import config


def generate_test_plan() -> Plan:
    processes = []
    id = 0
    tasks = []
    all_tasks = []
    amount_tasks = 20
    amount_processes = 3
    for i in range(amount_processes):
        for j in range(20):
            tasks.append(Task(id, j, 100, length_real=100))
            id += 1
        processes.append(Process(tasks, i))
        all_tasks += tasks
        tasks = []

    assert amount_tasks * amount_processes == len(all_tasks)
    return Plan(all_tasks, processes)


class TestPlan(unittest.TestCase):
    config.INS_PER_TICK = 10

    def test_generate_tasks_for_processes(self):
        tasks_pp = [10,20,30]
        sum_tasks = sum(tasks_pp)
        process_tasks = Plan.generate_tasks_for_processes(tasks_pp, 10, 100)
        num_all_tasks = 0
        for tasks in process_tasks:
            num_all_tasks += len(tasks)
        self.assertEqual(sum_tasks, num_all_tasks)

    def test_generate_tasks_for_processes(self):
        # python3 -m  unittest test_plan.TestPlan.test_generate_tasks_for_processes
        length_per_process = [10,20,25]
        min_len, max_len = 10, 20

        processes = Plan.generate_tasks_for_processes(length_per_process, min_len, max_len)

        # are number of tasks ok?
        tasks_sum = 0
        for p in processes:
            tasks_sum += len(p)
        self.assertEqual(sum(length_per_process), tasks_sum)

        # is last process for free slosts?
        self.assertTrue(processes[-1][0].process_id == -1)

    def test_generate_realistic_plan(self):
        # python3 -m  unittest test_plan.TestPlan.test_generate_realistic_plan
        tasks = [[],[]]
        number_tasks = 4
        for x in range(number_tasks):
            tasks[0].append(Task(0, 0, x))
            tasks[1].append(Task(1, 1, x))

        plan = Plan.generate_realistic_plan(tasks)

        self.assertEqual(number_tasks * 2, len(plan))
        for x in range(number_tasks*2-1):
            self.assertTrue(plan[x].process_id != plan[x+1].process_id)

        tasks = [[Task(0,0,0),  Task(0,0,1), Task(0,0,2)], [Task(1,1,3)]]
        plan = Plan.generate_realistic_plan(tasks)

        self.assertTrue(plan[0].process_id != plan[1].process_id)
        self.assertTrue(plan[2].process_id == plan[3].process_id)

    def test_generate_buffer_list(self):
        # python3 -m  unittest test_plan.TestPlan.test_generate_buffer_list
        tasks = [[Task(10, 0, 0), Task(10, 0, 0)], [Task(100, 1, 1)], [Task(10, -1, -1)]]
        buffers = Plan.generate_buffer_list(tasks, (100, 100))

        self.assertEqual(20, buffers[0])
        self.assertEqual(100, buffers[1])

    def test_generate_deadlines(self):

        tasks = [Task(10,0,0), Task(5,1,1), Task(10,-1,0), Task(5,1,3)]
        deadsies = Plan.generate_deadlines(tasks, (10,5))

        self.assertEqual(20, deadsies[0])
        self.assertEqual(35, deadsies[1])
