#!/usr/bin/env python3

from process import Threshold, ProcessRunner
from plan import Plan
import plan
import process

# TODO: lateness in time vs lateness in instructions
# TODO: task-IDs decreasing instead of increasing
# TODO: Visualisierung durchschnittlicher Threshold
# TODO: Mehrere Prozesse pro Job um Plan-Vorstellung besser zu entsprechen

# --- ADMIN STUFF ---
LOG = True
WRITE_PLAN = './plan'
JUST_GENERATE_PLAN = True

# --- CONFIGS ---
IPS = 4000000000
HZ = 250
INS_PER_TICK = IPS/HZ
SIGMA = 0.25
STRESS = 1
RELAX = 1
ANCHOR = IPS
RESCHEDULE_TIME = IPS
MAX_BUFF_USAGE = 0.2
TICKS_OFF = 10
MAX_TASK_DEVIAION = 2.0 # 200%

# --- PLAN CREATION ---
FREE_TIME = 10

NUMBER_PROCESSES = 3

TASK_MIN_LEN = IPS
TASK_MAX_LEN = IPS * 10

PROCESS_MIN_LEN = 10**1
PROCESS_MAX_LEN = 10**2

# % of whole Tasks that is added as buffer
BUFFER_MIN = 2
BUFFER_MAX = 10
LOAD = 1 #systemload



def run_sim():
    plan = Plan.generate_plan(NUMBER_PROCESSES,  PROCESS_MIN_LEN, PROCESS_MAX_LEN, TASK_MIN_LEN, TASK_MAX_LEN, BUFFER_MIN, BUFFER_MAX, FREE_TIME, file_path=WRITE_PLAN)
    task_lists_for_processes = sort_plan(plan)
    for i in range(len(task_lists_for_processes)):
        plan.process_info[i] = (task_lists_for_processes[i], plan.process_info[i][1] )
    processes = create_processes(plan.process_info)
    runner = create_process_runner(plan.task_list, processes)

    runner.write_plan_to_file("test.p")
    while not runner.has_finished() and not JUST_GENERATE_PLAN:
        runner.run_tick()



def create_processes(process_info):
    '''
    Creates processes according to the configuration given above.
    Process-Info is list of tuples [(<task-list>,buffer),...]
    '''
    processes = []
    for p in process_info:
        processes.append(Threshold(p[0], p[1]))
    return processes

def create_process_runner(task_list, processes):
    print("simulation initialized")
    return ProcessRunner(task_list, processes)

def sort_plan(plan: 'Plan') -> list:
    task_lists = [[] for p in range(len(plan.process_info))]
    for t in plan.task_list:
        if t.process_id == -1:
            continue
        else:
            task_lists[t.process_id].append(t)
    return task_lists

if __name__ == '__main__':
    plan.sigma = SIGMA
    process.ipt = INS_PER_TICK
    process.load = LOAD
    process.log = LOG
    process.hz = HZ
    process.max_buff_usg = MAX_BUFF_USAGE
    process.ticks_off = TICKS_OFF
    process.reschedule_time = RESCHEDULE_TIME
    process.max_task_deviation = MAX_TASK_DEVIAION

    run_sim()


#TODO: Context switches not included
