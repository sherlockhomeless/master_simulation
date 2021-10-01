import process
import task
import plan
from typing import Optional, List


def get_next_task_for_process(task_list: List[task.Task], p: process.Process) -> Optional[task.Task]:
    """
    Returns next task of process in the list
    :param task_list: the plan-task-list
    :param p: process to search for
    :return: Task or None
    """
    for t in task_list:
        if t.task_id == p.process_id:
            return t
    return None


def get_process_with_pid(pid: int, process_list: List[process.Process]) -> process.Process:
    return list(filter(lambda p: pid == p.process_id, process_list))[0]


def apply_stretch_real_length(p: plan.Plan, stretch: float, pid: Optional[int] = None):
    """
    Stretches the planned task length for a plan
    :param p: plan to be stretched
    :param stretch: stretch given as a float, no stretch is 1.0
    :param pid: Limits stretch to only one process if set
    :return: modified plan
    """
    tasks = p.task_list
    if pid is not None:
        tasks_to_stretch = list(filter(tasks, lambda t: t.process_id == pid))
    else:
        tasks_to_stretch = p.task_list

    for t in tasks_to_stretch:
        t.instructions.real = int(stretch * t.instructions.real)
    return p


class PlanFinishedException(Exception):
    pass

