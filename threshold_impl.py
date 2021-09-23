from typing import List
from process import Process
from task import Task
import config

"""
calc*-functions return int values indicating threshold values
check*-functions return bools, where true indicates that threshold was transgressed on
"""


def calc_t1(task: Task) -> int:
    """
    Calculates the t1 at which the currently running task is preempted and replaced by the next task in the plan.
    t1 is the minimum off two values, one of which represents an absolute boundary, the other a relative boundary:

        * max_global_deviation => is a global boundary that ensures that independant of the task details, a certain amount of ticks is not transgressed
        * max_local_deviation => is a local, relative boundary relating to the details of the task
    """

    cur_slot = task.get_current_slot_owner()
    instructions_planned = cur_slot.instructions.plan

    relative_t1 = int(instructions_planned * config.T1_SIGMA)
    t1_min = config.NO_PREEMPTION + instructions_planned
    t1_max = config.T1_MAX_VALUE + instructions_planned

    t1 = min(max(relative_t1, t1_min), t1_max)

    return t1


def compare_t1(instructions_retired_task: int, t1: int) -> int:
    return instructions_retired_task < t1


def calc_t2_task(ins_planned: int, stress: int) -> int:
    # calc different components
    t2_task_relative = int(ins_planned * config.T2_SIGMA)
    t2_task_min = ins_planned + config.T2_SPACER
    t2_task_max = ins_planned + config.T2_MAX
    t2_task = min(max(t2_task_relative, t2_task_min), t2_task_max)
    # hook into stress system
    t2_task += stress
    return int(t2_task)


def check_t2_task(instructions_retired_task: int, t2_task: int) -> bool:
    return instructions_retired_task > t2_task


def calc_t2_process(cur_process: Process, stress: int, task_list: List[Task]) -> (int,int):
    def calc_t2_process_buffers(process: Process, tasks_of_process: List[Task]):
        """
        Calculates the proportion of the buffer that is allowed to be used up
        """
        # calculate allowed capacity buffer
        cur_pid = process.process_id
        filter_pid = filter(lambda t: t.process_id == cur_pid, tasks_of_process)
        length_all_tasks = sum(filter_pid)
        capacity_buffer = int(length_all_tasks * (config.T2_CAPACITY_BUFFER - 1))

        # calculate allowed plan buffer
        process_completion = process.get_process_completion()
        plan_buffer = process.buffer
        capacity_buffer_deadline = int(plan_buffer * config.T2_CAPACITY_BUFFER - plan_buffer)
        capacity_buffer_per_process = capacity_buffer_deadline / config.NUMBER_PROCESSES
        cleared_plan_buffer = capacity_buffer_per_process * config.T2_AVAILABLE_PLAN_BUFFER
        allowed_plan_buffer = int(cleared_plan_buffer * process_completion)

        return capacity_buffer, allowed_plan_buffer

    t2_buffers = calc_t2_process_buffers(cur_process, task_list)
    t2_capacity_buffer = t2_buffers[0]
    t2_plan_buffer = t2_buffers[1]

    t2_plan = t2_plan_buffer + (stress * config.T2_STRESS_GAIN) - config.RESCHEDULE_TIME
    if t2_plan < config.T2_PROCESS_MINIMUM:
        t2_plan = config.T2_PROCESS_MINIMUM

    return t2_capacity_buffer, t2_plan


def check_t2_process(lateness_process: int, t2_process: (int, int)) -> bool:
    t2_capacity_buffer = t2_process[0]
    t2_plan_buffer = t2_process[1]

    if lateness_process < t2_capacity_buffer:
        return False
    return lateness_process > t2_plan_buffer


def calc_t2_node(instructions_planned_total: int, stress: int) -> int:

    t2_node_relative = instructions_planned_total * config.T2_NODE_LATENESS + (stress * config.T2_STRESS_GAIN) - config.RESCHEDULE_TIME
    t2_node = max(t2_node_relative, config.T2_NODE_LOWER_BOUND)
    return int(t2_node)


def check_t2_node(node_lateness: int, t2_node: int) -> bool:
    return node_lateness > t2_node


def check_t2_preemptions(task: Task) -> bool:
    return task.was_preempted >= config.T2_MAX_PREEMPTIONS


def calc_tm2_task(instructions_planned_task: int) -> int:
    tm2_task_relative: int = int(instructions_planned_task * config.TM2_SIGMA)
    tm2_task_max: int = max(tm2_task_relative, instructions_planned_task + config.TM2_TASK_SIGNALING_LIMIT)
    tm2_task: int = min(tm2_task_max, instructions_planned_task + config.TM2_TASK_SIGNALING_START)
    assert tm2_task < instructions_planned_task

    return tm2_task


def check_tm2_task(instructions_run_task: int, tm2: int) -> bool:
    return instructions_run_task > tm2


def calc_tm2_node(planned_instructions_finished: int) -> int:
    tm2_node_relative: int = int(planned_instructions_finished * config.TM2_NODE_EARLINESS_CAP)
    tm2_node = min(tm2_node_relative, config.TM2_NODE_LOWER_BOUND)
    return tm2_node


def check_tm2_node(node_lateness: int, tm2_node: int, stress: int) -> bool:
    return node_lateness < tm2_node or stress > 0


