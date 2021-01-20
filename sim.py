#!/usr/bin/env python3
from typing import Tuple, List
from process import Process
from plan import Plan
from task import Task
from process_runner import ProcessRunner
import plan
import process
import task
import process_runner
import thresholder

# TODO: lateness in time vs lateness in instructions
# BUG: Task_id generation is completely fucked; task 0-n on p0, n+1-m on p1,...
# TODO: PLAN: Plan is getting reversed, so short processes start late
# TODO: Visualisierung durchschnittlicher Threshold
# TODO: Mehrere Prozesse pro Job um Plan-Vorstellung besser zu entsprechen

# --- ADMIN STUFF ---
LOG = True
WRITE_PLAN = "logs/plan.log"
JUST_GENERATE_PLAN = False

# --- CONFIGS ---
IPS = 4000000000
HZ = 250
INS_PER_TICK = int(IPS/HZ)
SIGMA = 0.25
STRESS = 1
RELAX = 1
ANCHOR = IPS
RESCHEDULE_TIME = IPS / 20
MAX_BUFF_USAGE = 0.5
TICKS_OFF = 10
MAX_TASK_DEVIAION = INS_PER_TICK * 10
MAX_RELATIVE_DEVEATION = 1.3
DEADLINE = 1.1  # total time * DEADLINE = Time to be finished
MAX_TASK_OVERSTEP = 20
CAP_LATENESS = 1.5
SPACER_CONSTANT = 2
# --- PLAN CREATION ---
FREE_TIME = 10

NUMBER_PROCESSES = 3

TASK_MIN_LEN = INS_PER_TICK
TASK_MAX_LEN = INS_PER_TICK * 1000

PROCESS_MIN_LEN = 10
PROCESS_MAX_LEN = 10
# % of whole Tasks that is added as buffer
BUFFER_MIN = 2
BUFFER_MAX = 10
LOAD = 1  # systemload


def run_sim():
    new_plan = Plan.generate_plan(NUMBER_PROCESSES,  PROCESS_MIN_LEN, PROCESS_MAX_LEN,
                                  TASK_MIN_LEN, TASK_MAX_LEN, BUFFER_MIN, BUFFER_MAX, FREE_TIME, file_path=WRITE_PLAN)
    task_lists_for_processes = sort_plan(new_plan)

    runner = ProcessRunner(new_plan, ipt=INS_PER_TICK, log=LOG)
    runner.write_plan_to_file(WRITE_PLAN)
    while not runner.has_finished() and not JUST_GENERATE_PLAN:
        runner.run_tick()


def create_processes(process_info: List[Task], buffer: int, deadline: int) -> List[Process]:
    '''
    Creates processes according to the configuration given above.
    Process-Info is list of tuples [(<task-list>,buffer),...]
    '''
    processes = []
    for p in process_info:
        # tasklist, buffer, deadline
        processes.append(Process(p[0], p[1], p[2]))
    return processes


def sort_plan(plan: 'Plan') -> list:
    """
    Sorts all tasks of a long list of task into a list for each process.
    Input: [task0,task1,task2,...]
    Output:[[task0, task2], [task1,...],...] where the index is the process id
    """
    task_lists = [[] for p in range(len(plan.processes))]
    for t in plan.task_list:
        if t.process_id == -1:
            continue
        else:
            task_lists[t.process_id].append(t)
    return task_lists


if __name__ == '__main__':
    task.sigma = SIGMA
    task.ips = INS_PER_TICK
    process.ipt = INS_PER_TICK
    process.load = LOAD
    process.hz = HZ
    process.max_buff_usg = MAX_BUFF_USAGE
    process.ticks_off = TICKS_OFF
    process_runner.log = LOG
    thresholder.log = LOG
    thresholder.reschedule_time = RESCHEDULE_TIME
    thresholder.max_task_deviation = MAX_TASK_DEVIAION
    thresholder.max_relative_deviation = MAX_RELATIVE_DEVEATION
    thresholder.ipt = INS_PER_TICK
    thresholder.cap_lateness = CAP_LATENESS
    thresholder.consumable_buffer = MAX_BUFF_USAGE
    thresholder.spacer_constant = SPACER_CONSTANT
    process.deadline = DEADLINE
    process.max_task_overstep = MAX_TASK_OVERSTEP * INS_PER_TICK
    run_sim()


#TODO: Context switches not included
