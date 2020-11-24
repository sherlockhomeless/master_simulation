import unittest
from plan import Plan
from task import Task
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

    def test_plan_generation(self):
        generate_test_plan()
