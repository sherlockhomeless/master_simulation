import unittest
from plan import Plan
from task import Task
import task
from random import randint
from test_process import generate_test_process, generate_test_task

def generate_test_plan() -> Plan:
    processes = []
    id = 0
    tasks = []
    all_tasks = []
    amount_tasks = 20
    amount_processes = 3
    for i in range(amount_processes):
        for j in range(20):
            tasks.append(generate_test_task(id, j, 100, length_real=100))
            id += 1
        processes.append(generate_test_process(tasks, i))
        all_tasks += tasks
        tasks = []

    assert amount_tasks * amount_processes == len(all_tasks)
    return Plan(all_tasks, processes)


class TestPlan(unittest.TestCase):

    task.sigma = 1.1
    def test_plan_generation(self):
        generate_test_plan()

    def test_generate_tasks_for_processes(self):
        tasks_pp = [10,20,30]
        sum_tasks = sum(tasks_pp)
        process_tasks = Plan.generate_tasks_for_processes(tasks_pp, 10, 100)
        num_all_tasks = 0
        for tasks in process_tasks:
             num_all_tasks += len(tasks)


        self.assertEqual(sum_tasks, num_all_tasks)
