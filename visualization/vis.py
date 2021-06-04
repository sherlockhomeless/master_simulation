#!/usr/bin/env python3
from os import listdir
from os.path import join
from typing import List
import matplotlib.pyplot as plt

from log_parser import TickEvent, LogParser

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
    visualize_ticks(logs, ['t2_task', 't2_task_pure', 't2_process', 't2_node'], 't2_tick')

    print('visualizing latenesses')
    visualize_ticks(logs, ['lateness_task', 'lateness_process', 'lateness_node'], 'latenesses')

    print('printing plan and real lengths')
    visualize_plan_real_deviation(plan.Plan.read_plan_from_file(PLAN_LOG), 'compare_plan_real')


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


def visualize_plan_real_deviation(p: "Plan", figure_name: str =""):
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

