import process
import task
import plan
from typing import Optional, List


def get_next_task_for_process(task_list: List[task.Task], p: process.Process) -> Optional[task.Task]:
    for t in task_list:
        if t.task_id == p.process_id:
            return t
    return None


def get_process_with_pid(pid: int, process_list: List[process.Process]) -> process.Process:
    return list(filter(lambda p: pid == p.process_id, process_list))[0]


def apply_stretch_to_process(p: plan.Plan, stretch: float, pid: int = 0):
    for t in p:
        if t.process_id == pid:
            t.length_real = int(stretch * t.length_real)
    return p


class PlanFinishedException(Exception):
    pass

