#!/usr/bin/env python3
from os import listdir
from os.path import join
from typing import List
import matplotlib.pyplot as plt

import config
from log_parser import TickEvent, LogParser

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
visualize_plan = True


def vis():
    parsi = LogParser(UNIFIED_LOG)
    parsi.read_log()
    logs = parsi.get_parsed_logs()

    print("visualizing t1 per tick")
    visualize_ticks(logs, ['t1', 't1_pure'], "t1_tick")

    print('visualize t2 per tick')
    visualize_ticks(logs, ['t2_task', 't2_task_pure', 't2_process'], 't2_tick')


def visualize_ticks(logs: List[TickEvent], attributes: List[str], figure_name: str) -> None:
    """
    This functions visualizes the given attribute list and saves it with the given figure_name
    """
    vis_chronological(logs, attributes, figure_name=figure_name)


def vis_chronological(logs: List[TickEvent], threshold_types: List[str], figure_name=""):
    """
    Visualization of all thresholds which names are in thrshold_types
    """

    x = list(range(len(logs)))  # gets time axes

    # --- fill lists with corresponding data ---
    graph_labels = threshold_types
    thresh_values = [[] for x in range(len(threshold_types))]

    for line in logs:
        # picks for each selected threshold type the corresponding values out of the line
        for i, thresh_type in enumerate(threshold_types):
            event_tuple = line[thresh_type]
            thresh_values[i].append(event_tuple[1]/config.INS_PER_TICK)

    # --- Plot ---
    for i, graph in enumerate(threshold_types):
        plt.plot(x, thresh_values[i], label=graph_labels[i])

    plt.xlabel('timer tick')
    plt.ylabel('instructions per tick')
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

def check_disabled(line: TickEvent) -> List[str]:
    """
    Checks for NULL-values and returns the list of all disabled attributes
    :param line:
    :return:
    """


if __name__ == '__main__':
    vis()

