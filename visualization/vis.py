#!/usr/bin/env python3
from os import listdir
from os.path import join
from typing import List
import matplotlib.pyplot as plt

from log_parser import TickEvent, LogParser

import sys
sys.path.insert(0, '..')

import plan
import config

# TODO: Why list of logs, not just the required log?
# TODO: If thresholds were disabled, dont show them

"""
Threshold logging done in files of format thresh_[PROCESS_ID].log
"""


#  ---file names---
BASE_FOLDER = "/home/ml/Dropbox/Master-Arbeit/code/threshold_simulation"
LOG_FOLDER = join(BASE_FOLDER, "logs")  # Base-Folder for all log-files
PIC_FOLDER = join(BASE_FOLDER, "pics")  # Base-Folder for graphics
THRESH2_ALL = 'thresh2_all.log'  # all t2 logs of all processes
THRESH_CHRON = 'thresh_cron.log'  # chronological change of t1, t2, mt2
PLAN = "plan.log"
UNIFIED_LOG = join(LOG_FOLDER, 'unified_tick.log')
PLAN_LOG = join(LOG_FOLDER, PLAN)
visualize_plan = True


def vis():
    parsi = LogParser(UNIFIED_LOG)
    parsi.read_log()
    logs = parsi.get_parsed_logs()

    print("visualizing t1 per tick")
    visualize_ticks(logs, ['t1', 't1_pure'], "t1_tick")

    print('visualize t2 per tick')
    visualize_ticks(logs, ['t2_task', 't2_task_pure', 't2_process_capacity', 't2_process_plan',  't2_node'], 't2_tick')

    print('visualize t2_process and process_lateness')
    visualize_ticks(list(filter(lambda log: log.process_id[1] == 0, logs)), ['t2_process_capacity', 't2_process_plan', 'lateness_process'], 't2_process_tick')

    print('visualize t2 per tick without node')
    visualize_ticks(logs, ['t2_task', 't2_task_pure', 't2_process_capacity', 't2_process_plan'], 't2_tick_wo_node')

    print('visualizing latenesses')
    visualize_ticks(logs, ['lateness_task'], 'latenesses_task')
    visualize_ticks(logs, ['lateness_process'], 'latenesses_process')
    visualize_ticks(logs, ['lateness_node'], 'latenesses_node')

    print('visualize per process lateness')
    for i in range(2):
        cur_logs = list(filter(lambda l: l.process_id[1] == i, logs))
        visualize_ticks(cur_logs, ['lateness_process', 't2_process_plan'], f'lateness_p{i}')

    print('printing plan and real lengths')
    visualize_plan_real_deviation(plan.Plan.read_plan_from_file(PLAN_LOG), 'compare_plan_real')

    print('printing t1_task & t2_task for one process')
    visualize_t1_t2_per_process(logs, 0)

    print('visualizing t1 and lateness per task')
    visualize_t1(logs)


def visualize_t1_t2_per_process(logs: List[TickEvent], pid: int):
    """
    Filters the logs for only one process and then only the start tick for a task
    """
    only_one_pid = list(filter(lambda l: l.process_id[1] == pid, logs))
    filtered_logs = []
    seen_tids = set()
    for l in only_one_pid:
        if l.task_id[1] not in seen_tids:
            filtered_logs.append(l)
            seen_tids.add(l.task_id[1])

    x_axis = range(len(filtered_logs))
    plt.plot(x_axis, [y.t1[1]/config.INS_PER_TICK for y in filtered_logs], label='t1')
    plt.plot(x_axis, [y.t1_pure[1]/config.INS_PER_TICK for y in filtered_logs], label='t1 pure')
    plt.plot(x_axis, [y.t2_task[1]/config.INS_PER_TICK for y in filtered_logs], label='t2 task')
    plt.plot(x_axis, [y.t2_task_pure[1]/config.INS_PER_TICK for y in filtered_logs], label='t2 task pure')

    plt.xlabel('time ticks')
    plt.ylabel('instructions per tick')
    plt.legend()
    save_fig('t1_t2_process')


def visualize_ticks(logs: List[TickEvent], tracking_values: List[str], figure_name="", scale_to_IPT=True):
    """
    Visualization of all thresholds which names are in thrshold_types
    """

    x = list(range(len(logs)))  # gets time axes

    # --- fill lists with corresponding data ---
    graph_labels = tracking_values
    thresh_values = [[] for x in range(len(tracking_values))]

    for line in logs:
        # picks for each selected threshold type the corresponding values out of the line
        for i, thresh_type in enumerate(tracking_values):
            event_tuple = line[thresh_type]
            cur_value = event_tuple[1]/config.INS_PER_TICK if scale_to_IPT else event_tuple[1]
            thresh_values[i].append(cur_value)

    # --- Plot ---
    for i, graph in enumerate(tracking_values):
        plt.plot(x, thresh_values[i], label=graph_labels[i])

    plt.xlabel('timer tick')
    plt.ylabel('instructions per tick')
    plt.legend()
    save_fig(figure_name)


def visualize_plan_real_deviation(p: "Plan", figure_name: str = ""):
    plan_length = []
    real_length = []
    dif_length = []
    task_count = [x for x in range(len(p.task_list))]

    for t in p.task_list:
        plan_length.append(t.length_plan)
        real_length.append(t.length_real)
        dif_length.append((t.length_real - t.length_plan)/config.INS_PER_TICK)

    plt.plot(task_count, dif_length, label='real - length')

    plt.xlabel('task number')
    plt.ylabel('length IPT')
    plt.legend()
    save_fig(figure_name)


def visualize_t1(logs: List[TickEvent]):
    """
    Visualizes t1 including upper & lower bounds to lateness
    """
    logs = list(filter(lambda log: log.task_id[1] == 1, logs))
    x_axis = range(len(logs))
    plt.plot(x_axis, [config.NO_PREEMPTION/config.INS_PER_TICK] * len(logs), label='t1 lower bound')
    plt.plot(x_axis, [config.T1_MAX_VALUE/config.INS_PER_TICK] * len(logs), label='t1 upper bound')
    plt.plot(x_axis, [log.t1_pure[1]/config.INS_PER_TICK for log in logs], label='t1')
    plt.plot(x_axis, [log.lateness_task[1]/config.INS_PER_TICK for log in logs], label='lateness')
    plt.legend()
    save_fig('t1')


def save_fig(filename):
    plt.tight_layout()
    plt.savefig(f'{PIC_FOLDER}/{filename}.png', dpi=300)
    plt.clf()  # should clear all axis


def do_stat(threshs: List[TickEvent]) -> dict:
    stats = dict()
    for i, p in enumerate(threshs):
        minimum = min([x.t2 for x in p])
        stats[f'min_{i}'] = minimum
        maximum = max([x.t2 for x in p])
        stats[f'max_{i}'] = maximum

    return stats


def find_threshold_logs(pattern: str) -> List[str]:
    """
    find all threshold log files in LOG_FOLDER that contains the given pattern
    """
    files = listdir(LOG_FOLDER)
    logs = []
    for f in files:
        if pattern in f and ".log" in f:
            logs.append(f'{LOG_FOLDER}/{f}')
    logs.sort()
    print(f'[FIND] Found logs {logs} for pattern {pattern}')
    return logs


if __name__ == '__main__':
    vis()

