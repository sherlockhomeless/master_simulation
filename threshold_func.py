from process import Process
from task import Task
import config


def calc_t1(instructions_planned: int) -> int:
    """
    Calculates the t1 at which the currently running task is preempted and replaced by the next task in the plan.
    t1 is the minimum off two values, one of which represents an absolute boundary, the other a relative boundary:

        * max_global_deviation => is a global boundary that ensures that independant of the task details, a certain amount of ticks is not transgressed
        * max_local_deviation => is a local, relative boundary relating to the details of the task TODO: AND PROCESS
    """

    t1_relative_deviation = instructions_planned * config.T1_SIGMA
    t1_preemption_minimum = instructions_planned + config.NO_PREEMPTION
    relative_t1 = max(t1_relative_deviation, t1_preemption_minimum)

    t1 = int(min(relative_t1, config.T1_MAX_VALUE + instructions_planned))
    assert t1 > config.NO_PREEMPTION

    return t1


def compare_t1(instructions_retired_task: int, t1: int) -> int:
    return instructions_retired_task < t1


def calc_t2_task(ins_planned: int, t1: int) -> int:
    t2_task = ins_planned * config.T2_MAX_TASK_LATENESS
    t2_task = t1 + config.T2_SPACER if t2_task < t1 else t2_task
    assert t2_task > ins_planned and t2_task > t1
    return int(t2_task)


def check_t2_task(instructions_retired_task: int, t2_task: int) -> bool:
    return instructions_retired_task > t2_task


def calc_t2_process(cur_process: Process, stress: int) -> int:
    def calc_usable_buffer(process: Process, free_time=1.0):
        """
        Calculates the proportion of the buffer that is allowed to be used up
        """
        process_completion = process.instructions_executed / process.instructions_planned
        cleared_buffer = process.buffer * free_time
        available_buffer = cleared_buffer * config.ASSIGNABLE_BUFFER

        usable_buffer = available_buffer * process_completion

        if usable_buffer < config.T2_MINIMUM_USABLE_BUFFER * available_buffer:
            usable_buffer = config.T2_MINIMUM_USABLE_BUFFER * available_buffer

        assert usable_buffer < available_buffer
        assert usable_buffer >= 0  # t2 with 0% completion should just be one of other thresholds

        return int(usable_buffer)

    usable_buffer = calc_usable_buffer(cur_process, config.FREE_TIME)
    t2_p = usable_buffer + (stress * config.INS_PER_TICK) - config.RESCHEDULE_TIME
    t2_p = t2_p if t2_p > config.T2_PROCESS_MINIMUM else config.T2_PROCESS_MINIMUM

    assert t2_p > 0

    return int(t2_p)


def check_t2_process(lateness_process: int, t2_process) -> bool:
    return lateness_process > t2_process


def calc_t2_node(instructions_planned_total: int) -> int:
    if instructions_planned_total == 0:
        return
    t2_node = instructions_planned_total * config.T2_NODE_LATENESS
    return int(t2_node)


def check_t2_node(node_lateness: int, t2_node: int) -> bool:
    return node_lateness > t2_node


def check_t2_preemptions(task: Task) -> bool:
    return task.was_preempted >= config.T2_MAX_PREEMPTIONS


def calc_tm2_task(t2_task: int, instructions_planned_task: int) -> int:
    tm2_task_pure = t2_task - instructions_planned_task
    tm2_task = instructions_planned_task + tm2_task_pure

    assert tm2_task < instructions_planned_task

    return tm2_task


def check_tm2_task(instructions_run_task: int, tm2: int) -> bool:
    return instructions_run_task > tm2


def calc_tm2_node(t2_node: int) -> int:
    tm2_node = t2_node * -1 if t2_node is not None else -1
    return tm2_node


def check_tm2_node(node_lateness: int, tm2_node: int) -> bool:
    return node_lateness < tm2_node


