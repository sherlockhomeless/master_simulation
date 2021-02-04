import unittest
from typing import List

from process import Process
from task import Task


def generate_test_task(task_id, process_id, length_plan, length_real=None) -> Task:
    t = Task(length_plan, process_id, task_id) if length_real is None else Task(length_plan, process_id, task_id, length_real=length_real)
    return t


def generate_test_process(tasks: List[Task], id: int, buffer=0, deadline=0) -> Process:
    return Process(tasks, buffer, deadline)
